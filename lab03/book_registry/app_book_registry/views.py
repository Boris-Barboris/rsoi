import json

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed

# Create your views here.

from .rsoi_common import *
from .oauthclient import *
from .models import *


# GET /prints?isbn=<isbn>&title=<title>&author=<author>&page=X&size=Y 
# фильтрованный список книг

@log_view
@http_exception_guard
def prints(request):
    if request.method == 'GET':
        isbn = request.GET.get('isbn', None)
        title = request.GET.get('title', None)
        author = request.GET.get('author', None)
        prints = print_search(isbn, title, author)
        pp = paginate_list(prints, request)
        resp = HttpResponse(content = json.dumps(pp), 
            content_type='application/json', status=200)
        resp['X-total-count'] = str(len(prints))
        return resp
    else:
        return HttpResponseNotAllowed('405 Not allowed.')
        
# PUT /prints/<isbn> - зарегистрировать книгу.
# PATCH /prints/<isbn> - обновление параметров книги
# DELETE /prints/<isbn> - удаление книги

@log_view
@http_exception_guard
@authorize_request
def prints_isbn(request, me, isbn):
    if request.method == 'PUT':
        b = json.loads(request.body.decode('utf-8'))
        try:
            p = register_print(isbn, b)
            return HttpResponse(content = json.dumps(p.to_dict()), 
                content_type='application/json', status=201)
        except PrintAlreadyExists:
            return HttpResponse('441 Already exists.', status=441)
        except KeyError:
            return HttpResponseBadRequest('400 Malformed request.')
    elif request.method == 'PATCH':
        b = json.loads(request.body.decode('utf-8'))
        try:
            p = update_print(isbn, b)
            return HttpResponse(content = json.dumps(p.to_dict()), 
                content_type='application/json', status=200)
        except Print.DoesNotExist:
            return HttpResponse('404 Not found.', status=404)
    elif request.method == 'DELETE':
        try:
            delete_print(isbn, me)
            return HttpResponse('200 OK')
        except Print.DoesNotExist:
            return HttpResponse('404 Not found.', status=404)
        except BookExists:
            return HttpResponse('460 Book exists.', status=460)
    else:
        return HttpResponseNotAllowed('405 Not allowed.')