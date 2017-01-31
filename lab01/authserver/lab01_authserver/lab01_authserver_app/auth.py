from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django.shortcuts import render
from lab01_authserver_app.models import *
import json

import logging
log = logging.getLogger('lab01_authserver_app')


def auth_controller(request):
    log_request(request)
    if request.method == 'GET':
        oauth_params = oauth_params_auth(request)
        response = render(request, 'auth.html', {'oauth': oauth_params})
        log.debug('response:\n' + str(response.serialize()))
        return response
    else:
        return HttpResponseBadRequest('400 Malformed request.')

        
def login_controller(request):
    log_request(request)
    if request.method == 'POST':
        uname = request.POST.get('uname', None)
        password = request.POST.get('password', None)
        if 'register' in request.POST:
            operation = 'register'
        elif 'login' in request.POST:
            operation = 'login'
        else:
            return HttpResponseBadRequest('400 Malformed request')
        log.debug('request to {}, uname = {} password = {}'.format(operation, uname, password)) 
        if operation == 'login':
            user = authenticate(uname, password)
        elif operation == 'register':
            user = register_user(uname, password)
        else:                
            return HttpResponseBadRequest("400 Malformed request.")
        if user:
            # logged in OK, let's handle oauth case
            oauth = oauth_params_auth(request)
            if oauth and oauth['response_type'] == 'code':
                grant = issue_grantcode(user)
                redirect_uri = oauth['redirect_uri']
                redirect_uri += '?code=' + grant.code
                response = HttpResponseRedirect(redirect_uri)
            else:
                response = HttpResponseRedirect(reverse('users'))
                response.set_cookie('uname', uname)
                response.set_cookie('password', password)
            log.debug('response:\n' + str(response.serialize()))
            return response
        else:
            return HttpResponse('401 Unauthorized', status=401)
    else:
        return HttpResponseBadRequest('400 Malformed request.')
        

def users_controller(request):
    log_request(request)
    user = authorize_request(request)
    if not user:
        return HttpResponse('401 Unauthorized', status=401)
    # now check if we perform some post operations
    if request.method == 'POST':
        delete_uname = request.POST['delete']
        log.debug('request to delete user ' + delete_uname)
        delete_user(delete_uname)
        return HttpResponseRedirect(reverse('users'))
    users = list_users()
    return render(request, 'users.html', {'users': users})
    
    
def users_controller_me(request):
    log_request(request)
    try:
        user = authorize_request(request)
    except AccessTokenExpired:
        return HttpResponse('440 Token expired', status=440)
    if not user:
        return HttpResponse('401 Unauthorized', status=401)
    else:
        content = {'uname': user.uname}
        response = HttpResponse(content = json.dumps(content), 
                content_type='application/json', status=200)
        log.debug('response:\n' + str(response.serialize()))
        return response
        
        
def users_controller_list(request):
    log_request(request)
    try:
        user = authorize_request(request)
    except AccessTokenExpired:
        return HttpResponse('440 Token expired', status=440)
    if not user:
        return HttpResponse('401 Unauthorized', status=401)
    else:
        users = list_users()
        content = [u.uname for u in uers]
        response = HttpResponse(content = json.dumps(content), 
                content_type='application/json', status=200)
        log.debug('response:\n' + str(response.serialize()))
        return response
    
    
def token_controller_issue(request):
    # here we need to issue access and refresh tokens via grant code
    log_request(request)
    oauth = oauth_params_token_issue(request)
    if oauth and oauth['grant_type'] == 'authorization_code':
        try:
            user = authenticate_authcode(oauth['code'])
        except AuthGrantCodeExpired:
            return HttpResponse('440 grant code expired', status=440)
        if user:
            tokens = issue_tokens(user, oauth['client_id'])
            # now let's form the response
            content = {}
            content['token_type'] = 'mytokentype'
            content['expires_in'] = atoken_lifetime
            content['access_token'] = tokens['atoken'].token
            content['refresh_token'] = tokens['rtoken'].rtoken
            response = HttpResponse(content = json.dumps(content), 
                content_type='application/json', status=200)
            log.debug('response:\n' + str(response.serialize()))
            return response
        return HttpResponse('401 Unauthorized', status=401)
    return HttpResponseBadRequest('400 Malformed request.')
    

def token_controller_verify(request):
    log_request(request)
    atoken = request.POST.get('access_token', None)
    if atoken:
        try:
            user = authenticate_token(atoken)
        except AccessTokenExpired:
            return HttpResponse('Token expired', status=440)
        if user:
            return HttpResponse('OK', status=200)
        else:
            return HttpResponse('404 Not found', status=404)
    return HttpResponseBadRequest('400 Malformed request.')
    
    
def token_controller_refresh(request):
    # here we need to issue access and refresh tokens via grant code
    log_request(request)
    oauth = oauth_params_token_refresh(request)
    if oauth and oauth['grant_type'] == 'refresh_token':
        user = authenticate_rtoken(oauth['refresh_token'])
        if user:
            tokens = issue_tokens(user, oauth['client_id'])
            # now let's form the response
            content = {}
            content['token_type'] = 'mytokentype'
            content['expires_in'] = atoken_lifetime
            content['access_token'] = tokens['atoken'].token
            content['refresh_token'] = tokens['rtoken'].rtoken
            response = HttpResponse(content = json.dumps(content), 
                content_type='application/json', status=200)
            log.debug('response:\n' + str(response.serialize()))
            return response
        return HttpResponse('401 Unauthorized', status=401)
    return HttpResponseBadRequest('400 Malformed request.')
    
    
def token_controller_grant(request):
    # this is debug endpoint to issue grant codes without redirect stuff
    log_request(request)
    uname = request.POST.get('uname', None)
    password = request.POST.get('password', None)
    user = authenticate(uname, password)
    if user:
        # logged in OK, let's handle oauth case
        grant = issue_grantcode(user)
        response = HttpResponse(grant.code, status=200)
        log.debug('response:\n' + str(response.serialize()))
        return response
    else:
        return HttpResponse('401 Unauthorized', status=401)
    

def query_string(params):
    str = '?'
    for k in params:
        if len(str) > 1:
            str = str + '&'
        str = str + k + '=' + params[k]
    return str
    
def log_request(request):
    log.debug(str(request))
    log.debug('GET: ' + str(request.GET))
    log.debug('POST: ' + str(request.POST))
    log.debug('Cookies:\n' + repr(request.COOKIES))
    #log.debug('Meta:\n' + repr(request.META))
    
def authorize_request(request):
    # fist try cookies
    uname = request.COOKIES.get('uname', None)
    password = request.COOKIES.get('password', None)
    user = authenticate(uname, password)
    if user:
        return user
    else:
        # now let's try AccessToken
        access_token = request.META.get('access_token', None)
        if access_token:
            user = authenticate_token(access_token)
            return user
    return None
    
def oauth_params_auth(request):
    d = rdict(request)
    oauth = {}
    try:
        oauth['response_type'] = d['response_type']
        oauth['client_id'] = d['client_id']
        oauth['redirect_uri'] = d['redirect_uri']
        return oauth
    except:
        return None
        
def oauth_params_token_issue(request):
    d = rdict(request)
    oauth = {}
    try:
        oauth['grant_type'] = d['grant_type']
        oauth['client_id'] = d['client_id']
        oauth['client_secret'] = d['client_secret']
        oauth['redirect_uri'] = d['redirect_uri']
        oauth['code'] = d['code']
        return oauth
    except:
        return None
        
def oauth_params_token_refresh(request):
    d = rdict(request)
    oauth = {}
    try:
        oauth['grant_type'] = d['grant_type']
        oauth['client_id'] = d['client_id']
        oauth['client_secret'] = d['client_secret']
        oauth['refresh_token'] = d['refresh_token']
        return oauth
    except:
        return None
        
def rdict(request):
    if request.method == 'GET':
        return request.GET
    elif request.method == 'POST':
        return request.POST
    return None