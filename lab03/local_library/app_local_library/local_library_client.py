import json
import requests

#from .rsoi_common import *
from .oauthclient import *


class LocalLibError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

        
        
class LocalLibClient():
    def __init__(self, url, auth_client):
        self.url = url
        self.auth_client = auth_client
        self.s = requests.Session()
        
    def books_status(self, isbn):
        r = self.s.get(self.url + '/books/status/', params = {'isbn': isbn})
        if r.status_code == 200:
            return bool(r.text)
        else:
            raise LocalLibError(repr(r))
        
    def _authed_request_refresh(self, refresh, method, *args, **kwargs):
        atoken = self.auth_client.get_token()
        headers = {'ACCESSTOKEN': atoken}
        k_headers = kwargs.get('headers', {})
        k_headers.update(headers)
        kwargs['headers'] = k_headers
        r = method(*args, **kwargs)
        if r.status_code == 403:
            raise ForbiddenException('server returned 403 Forbidden')
        elif r.status_code == 401:
            raise UnauthorizedException('server returned 401 Unauthorized')
        elif refresh and r.status_code == 440:
            self.auth_client.issue_tokens()
            return _authed_request_refresh(self, False, method, *args, **kwargs)
        else:
            return r
            
    def _authed_request(self, method, *args, **kwargs):
        return self._authed_request_refresh(True, method, *args, **kwargs)
        
    def books_list(self, isbn=None, page=0, size=None):
        params = {}
        if isbn:
            params['isbn'] = isbn
        if size and size > 0:
            params['page'] = page
            params['size'] = size
        r = self._authed_request(self.s.get, self.url + '/books/', params = params)
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            raise LocalLibError(repr(r))
            
    def add_book(self, id, isbn):
        b = {'isbn': isbn}
        r = self._authed_request(self.s.put, self.url + '/books/' + str(id) + '/', 
            json=b)
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            raise LocalLibError(repr(r))
            
    def delete_book(self, id):
        r = self._authed_request(self.s.delete, self.url + '/books/' + str(id) + '/')
        if r.status_code == 200:
            return None
        else:
            raise LocalLibError(repr(r))
            
    def get_book(self, id):
        r = self._authed_request(self.s.get, self.url + '/books/' + str(id) + '/')
        if r.status_code == 200:
            return r.json()
        else:
            raise LocalLibError(repr(r))
            
    def borrow_book(self, id, borrow_id):
        uri = self.url + '/books/{}/borrow/{}/'.format(id, borrow_id)
        r = self._authed_request(self.s.post, uri)
        if r.status_code == 200:
            return r.json()
        else:
            raise LocalLibError(repr(r))
            
    def return_book(self, id):
        uri = self.url + '/books/{}/return/'.format(id)
        r = self._authed_request(self.s.post, uri)
        if r.status_code == 200:
            return r.json()
        else:
            raise LocalLibError(repr(r))