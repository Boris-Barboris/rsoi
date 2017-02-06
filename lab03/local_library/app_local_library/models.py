from django.db import models
import json

# Create your models here.

class Book(models.Model):
    isbn = models.CharField(max_length=20, blank=False)    
    BORROWED = 'brwed'
    FREE = 'free'
    state_choices = (
        (BORROWED, 'borrowed'),
        (FREE, 'free'),
    )
    state = models.CharField(max_length=20, choices=state_choices, default=FREE)
    borrow_id = models.IntegerField(null=True, default=None)
    
    def to_dict(self):
        return {
            'id':       self.id,
            'isbn':     self.isbn,
            'state':    self.state,
            'borrow_id':    self.borrow_id,
        }
        
    def to_json(self):
        return json.dumps(self.to_dict())
        
# exceptions

class AlreadyExists(Exception):
    def __init__(self, id):
        Exception.__init__(self, 'Book id={} already exists'.format(id))
        self.id = id

class AlreadyBorrowed(Exception):
    def __init__(self, id):
        Exception.__init__(self, 'Book id={} is already borrowed'.format(id))
        self.id = id
        
class AlreadyFree(Exception):
    def __init__(self, id):
        Exception.__init__(self, 'Book id={} is already free'.format(id))
        self.id = id
        
# model operations

def get_status(isbn):
    free_books = Book.objects.filter(isbn=isbn).filter(state=Book.FREE)    
    if len(free_books) > 0:
        return True
    else:
        return False
        
def create_book(id, isbn):
    # isbn validation should be here
    try:
        book = Book.objects.get(id=id)
        raise AlreadyExists(id)
    except Book.DoesNotExist:
        book = Book(id=id, isbn=isbn)
        book.save()
        return book
    
def delete_book(id):
    book = Book.objects.get(id=id)
    book.delete()
    
def get_book(id):
    book = Book.objects.get(id=id)
    return book
    
def get_books_isbn(isbn):
    books = Book.objects.filter(isbn=isbn)
    return books
    
def get_books():
    return Book.objects.all()
    
def borrow_book(id, borrow_id):
    book = Book.objects.get(id=id)
    if book.state == Book.FREE:
        book.borrow_id = borrow_id
        book.state = Book.BORROWED
        book.save()
    else:
        raise AlreadyBorrowed(id)
        
def return_book(id):
    book = Book.objects.get(id=id)
    if book.state == Book.BORROWED:
        book.borrow_id = None
        book.state = Book.FREE
        book.save()
    else:
        raise AlreadyFree(id)