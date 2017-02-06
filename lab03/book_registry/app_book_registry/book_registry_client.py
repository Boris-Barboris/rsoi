import json
import requests

from .rsoi_common import HttpOauthClient, AlreadyExists
from .oauthclient import *


class BookRegistryError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
        
        
class BookRegistryClient(HttpOauthClient):
    
    def list_prints(self, isbn = None, title = None, author = None,
            page = 0, size = None):
        params = {}
        if isbn:
            params['isbn'] = isbn
        if title:
            params['title'] = title
        if author:
            params['author'] = author
        if size and size > 0:
            params['page'] = page
            params['size'] = size
        r = self.s.get(self.url + '/prints/', params = params)
        if r.status_code == 200:
            return {'list': json.loads(r.text), 
                    'total': int(r.headers['X-total-count'])}
        else:
            raise BookRegistryError(repr(r) + str(r.content))
            
    def add_print(self, isbn, print_params):
        r = self._authed_request(self.s.put, self.url + '/prints/' + isbn + '/', 
            json=print_params)
        if r.status_code == 201:
            return json.loads(r.text)
        elif r.status_code == 441:
            raise AlreadyExists(repr(r) + str(r.content))
        else:
            raise BookRegistryError(repr(r) + str(r.content))
            
    def update_print(self, isbn, print_params):
        r = self._authed_request(self.s.patch, self.url + '/prints/' + isbn + '/', 
            json=print_params)
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            raise BookRegistryError(repr(r) + str(r.content))
            
    def delete_print(self, isbn):
        r = self._authed_request(self.s.delete, self.url + '/prints/' + isbn + '/')
        if r.status_code != 200:
            raise BookRegistryError(repr(r) + str(r.content))