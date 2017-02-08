import json

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, \
    HttpResponseNotAllowed, HttpResponseRedirect
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction

# Create your views here.

from .rsoi_common import *
from .oauthclient import *
from .models import *
from .clients import *

import logging
log = logging.getLogger('app_logging')

# decorator to manage auth context tokens
def grant_login(f):
    def get_auth(r, *args, **kwargs):
        auth = r.session.get('auth', None)
        if auth is None:
            grant = r.GET.get('code', None)
            if grant:
                auth = {'grant': grant}
                # now let's authorize
                ac = oauth_client_grant(grant, settings.USR_PORTAL_REDIRECT)
                act = ac.make_token_client()
                auth['me'] = act.me()
                auth['auth_url'] = act.auth_url + '/auth'
                auth['tokens'] = act.auth_plugin.token_raw
                r.session['auth'] = auth
                auth = dict(auth)
                auth['client'] = act
                log.debug('====session.auth==== ' + repr(auth))
        elif auth.get('tokens', None):
            tokens = auth['tokens']
            act = oauth_client(tokens['access_token'], tokens['refresh_token'])
            auth = dict(auth)
            auth['client'] = act
        return f(r, auth, *args, **kwargs)
    return get_auth

# GET /

@log_view
@http_exception_guard
@grant_login
def root(request, auth):
    if request.method == 'GET':
        return redirect('prints_stored')
    else:
        return HttpResponseNotAllowed('405 Not allowed.')
        

# GET /login?code=<code>

@log_view
@http_exception_guard
@grant_login
def login(request, auth):
    if request.method == 'GET':
        if not auth or (not 'tokens' in auth):
            auth_url = 'http://' + settings.AUTH_SERVER + '/auth'
            auth_url += '?response_type=code&client_id={}&redirect_uri={}'.\
                format(settings.CLIENT_ID, settings.USR_PORTAL_REDIRECT)
            log.debug('REDIRECT URI = ' + auth_url)
            return HttpResponseRedirect(auth_url)
        else:
            return redirect('prints_stored')
    else:
        return HttpResponseNotAllowed('405 Not allowed.')
       
# GET /logout
       
@log_view
@http_exception_guard
def logout(request):
    if request.method == 'GET':
        request.session.pop('auth', None)
        return redirect('prints_stored')
    else:
        return HttpResponseNotAllowed('405 Not allowed.')

# GET /prints/stored?isbn=<isbn>&title=<title>&author=<author>&page=X&size=Y
        
@log_view
@http_exception_guard
@grant_login
def prints_stored(request, auth):
    if request.method == 'GET':
        context = {'auth': auth}
        # now let's list free books
        if auth and auth.get('tokens', None):
            # we are authorized
            lc = local_library_client(None, auth['client'])
            bc = book_registry_client(None, auth['client'])
            page = request.GET.get('page', 0)
            size = request.GET.get('size', 10)
            context['page'] = page
            context['size'] = size
            prints = bc.list_prints()
            free_prints = [p for p in prints['list'] if lc.books_status(p['isbn'])]
            paginator = Paginator(free_prints, size)
            try:
                prints_page = paginator.page(page)
            except PageNotAnInteger:
                prints_page = paginator.page(1)
            except EmptyPage:
                prints_page = paginator.page(paginator.num_pages)
            context['prints'] = prints_page
            context['show_prints'] = True
        return render(request, 'prints.html', context)
    else:
        return HttpResponseNotAllowed('405 Not allowed.')
        

@log_view
@http_exception_guard
@grant_login
def borrows(request, auth):
    if request.method == 'GET':
        context = {'auth': auth}
        # now let's list free books
        if auth and auth.get('tokens', None):
            # we are authorized
            lc = local_library_client(None, auth['client'])
            bc = book_registry_client(None, auth['client'])
            page = request.GET.get('page', 0)
            size = request.GET.get('size', 10)
            context['page'] = page
            context['size'] = size
            borrows = list_user_borrows(auth['me']['uname'])
            for b in borrows:
                # let's add book title to dict for visual fidelity (slow)
                book = lc.get_book(b['book_id'])
                p = bc.list_prints(isbn=book['isbn'])['list'][0]
                b['title'] = p['title']
            paginator = Paginator(borrows, size)
            try:
                borrows_page = paginator.page(page)
            except PageNotAnInteger:
                borrows_page = paginator.page(1)
            except EmptyPage:
                borrows_page = paginator.page(paginator.num_pages)
            context['borrows'] = borrows_page
            context['show_borrows'] = True
        return render(request, 'borrows.html', context)
    else:
        return HttpResponseNotAllowed('405 Not allowed.')
        

@log_view
@http_exception_guard
@grant_login
def borrow(request, auth, isbn):
    if request.method == 'POST':
        context = {'auth': auth}
        # now let's list free books
        if auth and auth.get('tokens', None):
            # we are authorized
            try:
                b = borrow_print(isbn, auth)
                return redirect('prints_stored')
            except PrintDoesNotExist:
                return HttpResponse('404 Print not found.', status=404)
            except NoFreeBooks:
                return HttpResponse('450 No free books.', status=450)
            except AlreadyBorrowed:
                return HttpResponse('451 Already borrowed.', status=451)
        else:
            return HttpResponse('401 Unauthorized', status=401)
    else:
        return HttpResponseNotAllowed('405 Not allowed.')
        

@log_view
@http_exception_guard
@grant_login
def do_return(request, auth, borrow_id):
    if request.method == 'POST':
        context = {'auth': auth}
        # now let's list free books
        if auth and auth.get('tokens', None):
            # we are authorized
            b = return_borrow(borrow_id, auth)
            return redirect('borrows')
        else:
            return HttpResponse('401 Unauthorized', status=401)
    else:
        return HttpResponseNotAllowed('405 Not allowed.')