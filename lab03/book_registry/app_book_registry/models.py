from django.db import models
from django.conf import settings

import json
import logging
import datetime
import re

from .clients import *

log = logging.getLogger('app_logging')

# Create your models here.

class Print(models.Model):
    isbn = models.CharField(max_length=20, blank=False, null=False, primary_key=True)
    title = models.CharField(max_length=200, blank=False, null=False)
    page_count = models.IntegerField(null=False)
    authors = models.CharField(max_length=200, blank=True, null=False)
    year = models.IntegerField(null=True, default=None)
        
    def to_dict(self):
        return {
            'isbn':         self.isbn,
            'title':        self.title,
            'authors':      self.authors,
            'page_count':   self.page_count,
            'year':         self.year,
        }
    
# exceptions

class PrintAlreadyExists(Exception):
    def __init__(self, isbn):
        Exception.__init__(self, 'Print isbn={} already exists'.format(isbn))
        self.isbn = isbn
        
class BookExists(Exception):
    def __init__(self, isbn):
        Exception.__init__(self, 'Print isbn={} has existing books in local ' + \
            'library and cannot be deleted.'.format(isbn))
        self.isbn = isbn

# model operations

def print_search(isbn = None, title = None, author = None):
    if isbn:
        try:
            prints = Print.objects.get(isbn=isbn)
            return [prints.to_dict()]
        except Print.DoesNotExist:
            return []
    if title is None:
        title = '.+'
    if author is None:
        author = '.+'
    title_matched = Print.objects.filter(title__iregex=title)
    author_matched = title_matched.filter(authors__iregex=author)
    return [p.to_dict() for p in author_matched]
    
def register_print(isbn, params):
    try:
        print = Print.objects.get(isbn=isbn)
        raise PrintAlreadyExists(isbn)
    except Print.DoesNotExist:
        print = Print(isbn=isbn, title=params['title'], 
            page_count=params['page_count'], authors=params['authors'], 
            year=params.get('year', None))
        print.save()
        return print
        
def update_print(isbn, params):
    print = Print.objects.get(isbn=isbn)
    #log.debug('====params====' + repr(params))
    if 'title' in params:
        print.title = params['title']
    if 'authors' in params:
        print.authors = params['authors']
    if 'page_count' in params:
        print.page_count = params['page_count']
    if 'year' in params:
        print.year = params['year']
    print.save()
    return print
    
def delete_print(isbn, me):
    print = Print.objects.get(isbn=isbn)
    # cannot delete when there are books of this type
    token = me['token']
    lc = local_library_client(token)
    books = lc.books_list(isbn=isbn)
    if books['total'] > 0:
        raise BookExists(isbn)
    print.delete()
    