import json
import requests

from .rsoi_common import HttpOauthClient, AlreadyExists
from .oauthclient import *


class LocalLibError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
        
        
class LocalLibClient(HttpOauthClient):
        
    def books_status(self, isbn):
        r = self.s.get(self.url + '/books/status/', params = {'isbn': isbn})
        if r.status_code == 200:
            return r.text == "True"
        else:
            raise LocalLibError(repr(r))
        
    def books_list(self, isbn=None, page=0, size=None):
        params = {}
        if isbn:
            params['isbn'] = isbn
        if size and size > 0:
            params['page'] = page
            params['size'] = size
        r = self._authed_request(self.s.get, self.url + '/books/', params = params)
        if r.status_code == 200:
            return {'list': json.loads(r.text), 
                    'total': int(r.headers['X-total-count'])}
        else:
            raise LocalLibError(repr(r) + str(r.content))
            
    def add_book(self, id, isbn):
        b = {'isbn': isbn}
        r = self._authed_request(self.s.put, self.url + '/books/' + str(id) + '/', 
            json=b)
        if r.status_code == 201:
            return json.loads(r.text)
        elif r.status_code == 441:
            raise AlreadyExists(repr(r) + str(r.content))
        else:
            raise LocalLibError(repr(r) + str(r.content))
            
    def delete_book(self, id):
        r = self._authed_request(self.s.delete, self.url + '/books/' + str(id) + '/')
        if r.status_code == 200:
            return None
        else:
            raise LocalLibError(repr(r) + str(r.content))
            
    def get_book(self, id):
        r = self._authed_request(self.s.get, self.url + '/books/' + str(id) + '/')
        if r.status_code == 200:
            return r.json()
        else:
            raise LocalLibError(repr(r) + str(r.content))
            
    def borrow_book(self, id, borrow_id):
        uri = self.url + '/books/{}/borrow/{}/'.format(id, borrow_id)
        r = self._authed_request(self.s.post, uri)
        if r.status_code == 200:
            return r.json()
        else:
            raise LocalLibError(repr(r) + str(r.content))
            
    def return_book(self, id):
        uri = self.url + '/books/{}/return/'.format(id)
        r = self._authed_request(self.s.post, uri)
        if r.status_code == 200:
            return r.json()
        else:
            raise LocalLibError(repr(r) + str(r.content))