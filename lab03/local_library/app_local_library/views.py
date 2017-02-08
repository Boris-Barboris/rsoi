import json

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed

# Create your views here.

from .rsoi_common import *
from .oauthclient import *
from .models import *


# GET /books/status?isbn=<isbn> - проверить наличие книги

@log_view
@http_exception_guard
def books_status(request):
    if request.method == 'GET':
        isbn = request.GET.get('isbn', None)
        if isbn:
            return HttpResponse(str(get_status(isbn)))
        else:
            return HttpResponseBadRequest('400 Malformed request.')
    else:
        return HttpResponseNotAllowed('405 Not allowed.')


# GET /books?isbn=<isbn>&page=X&size=Y - список книг с фильтрацией и пагинацией
        
@log_view
@http_exception_guard
def books(request):
    if request.method == 'GET':
        return _books(request)
    else:
        return HttpResponseNotAllowed('405 Not allowed.')
        
@authorize_request
def _books(request, me):
    isbn = request.GET.get('isbn', None)
    if isbn:
        books = get_books_isbn(isbn)
    else:
        books = get_books()
    pbooks = paginate_list(books, request)
    pbooks_dicts = [b.to_dict() for b in pbooks]
    resp = HttpResponse(content = json.dumps(pbooks_dicts), 
                content_type='application/json', status=200)
    resp['X-total-count'] = str(len(books))
    return resp
    
    
# PUT /books/<id>?isbn=<isbn> - новая книга
# DELETE /books/<id> - удалить книгу
# GET /books/<id> - информация по книге

@log_view
@http_exception_guard
@authorize_request
def books_id(request, me, id):
    if request.method == 'PUT':
        b = json.loads(request.body.decode('utf-8'))
        if not 'isbn' in b:
            return HttpResponseBadRequest('400 Malformed request.')
        else:
            try:
                create_book(id, b['isbn'], me)
                res = get_book(id)
                return HttpResponse(content = json.dumps(res.to_dict()), 
                    content_type='application/json', status=201)
            except BookAlreadyExists:
                return HttpResponse('441 Already exists.', status=441)
            except PrintDoesNotExist:
                return HttpResponse('442 Print does not exist.', status=442)
    elif request.method == 'DELETE':
        delete_book(id)
        return HttpResponse()
    elif request.method == 'GET':
        res = get_book(id)
        return HttpResponse(content = json.dumps(res.to_dict()), 
            content_type='application/json', status=200)
    else:
        return HttpResponseNotAllowed('405 Not allowed.')


#POST /books/<id>/borrow/<borrow_id> - выдать книгу
            
@log_view
@http_exception_guard
def book_borrow(request, id, borrow_id):
    if request.method == 'POST':
        return _book_borrow(request, id, borrow_id)
    else:
        return HttpResponseNotAllowed('405 Not allowed.')

@authorize_request        
def _book_borrow(request, me, id, borrow_id):
    try:
        borrow_book(id, borrow_id)
        res = get_book(id)
        return HttpResponse(content = json.dumps(res.to_dict()), 
            content_type='application/json', status=200)
    except AlreadyBorrowed:
        return HttpResponse('Already borrowed', status=450)
        

# POST /books/<id>/return - вернуть книгу
        
@log_view
@http_exception_guard
def book_return(request, id):
    if request.method == 'POST':
        return _book_return(request, id)
    else:
        return HttpResponseNotAllowed('405 Not allowed.')

@authorize_request        
def _book_return(request, me, id):
    try:
        return_book(id)
        res = get_book(id)
        return HttpResponse(content = json.dumps(res.to_dict()), 
            content_type='application/json', status=200)
    except AlreadyFree:
        return HttpResponse('Already free', status=451)
    