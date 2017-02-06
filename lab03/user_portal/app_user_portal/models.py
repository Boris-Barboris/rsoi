from django.db import models
from django.utils import timezone

# Create your models here.

import json
import logging

from .clients import *
from .local_library_client import AlreadyBorrowed

log = logging.getLogger('app_logging')

class User(models.Model):
    uname = models.CharField(max_length=100, primary_key=True)
    first_borrow = models.DateTimeField(auto_now_add = True)
    
    def to_dict(self):
        return {'uname': self.uname,
                'first_borrow': self.first_borrow,
               }
               
class Borrow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book_id = models.IntegerField(null=True, default=None)
    start_date = models.DateTimeField(auto_now_add = True)
    
    OPEN = 'open'
    CLOSED = 'closed'
    state_choices = (
        (OPEN, 'open'),
        (CLOSED, 'closed'),
    )
    state = models.CharField(max_length=10, choices=state_choices, default=OPEN)
    
    def to_dict(self):
        return {
            'id':           self.id,
            'user':         self.user.uname,
            'book_id':      self.book_id,
            'start_date':   self.start_date,
            'state':        self.state,
        }
        
        
# exceptions

class PrintDoesNotExist(Exception):
    def __init__(self, isbn):
        Exception.__init__(self, 'Print isbn={} does not exist'.format(isbn))
        self.isbn = isbn
        
class NoFreeBooks(Exception):
    def __init__(self):
        Exception.__init__(self, 'No free books found')
        

# model operations

def log_user(uname):
    try:
        user = User.objects.get(uname=uname)
        return user
    except User.DoesNotExist:
        user = User()
        user.uname = uname
        user.save()
        return user

# borrow book
def borrow_print(isbn, auth):
    lc = local_library_client(None, auth['client'])
    bc = book_registry_client(None, auth['client'])
    prints = bc.list_prints(isbn=isbn)
    if len(prints) == 0:
        raise PrintDoesNotExist(isbn)
    books = lc.books_list(isbn=isbn)
    free_books = [b for b in books['list'] if b['state'] == 'free']
    if len(free_books) == 0:
        raise NoFreeBooks()
    free_book = free_books[0]   # book chosen
    borrow = Borrow()
    borrow.user = log_user(auth['me']['uname'])
    borrow.save()
    try:
        lc.borrow_book(free_book['id'], borrow.id)
        borrow.book_id = free_book['id']
        borrow.save()
        return borrow.to_dict()
    except:
        borrow.delete()
        raise
    
def return_borrow(borrow_id, auth):
    lc = local_library_client(None, auth['client'])
    borrow = Borrow.objects.get(id=borrow_id)
    lc.return_book(borrow.book_id)
    borrow.state = Borrow.CLOSED
    borrow.save()
    return borrow.to_dict()
    
def list_user_borrows(uname):
    borrows = Borrow.objects.filter(user__uname=uname)
    return [b.to_dict() for b in borrows]
        