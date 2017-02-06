#!/usr/bin/python3

from app_local_library.oauthclient import *
from app_local_library.local_library_client import *
import json
import requests
import logging
import http.client

http.client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


pp = PasswordPlugin('admin', 'admin')
client = OAuthClient('http://127.0.0.1:39000', pp, 'debug_client', 'mysecret', 'localhost')
print('\nVerification using password plugin\n')
print('\n\n' + repr(client.verify()) + '\n')
print('\nissuing tokens...\n')
tokens = client.get_token()
print('\n\ntoken:\n')
print('\n' + repr(tokens) + '\n')

ll = LocalLibClient('http://localhost:39002', client)

print('\nlist free...\n')
print('\n\n' + repr(ll.books_status('10000')) + '\n')

print('\nlist books...\n')
print('\n\n' + repr(ll.books_list()) + '\n')

print('\ncreating test books...\n')
print('\n\n' + repr(ll.add_book(1337, '10000')) + '\n')
print('\n\n' + repr(ll.add_book(1338, '10000')) + '\n')
print('\n\n' + repr(ll.add_book(1339, '10000')) + '\n')

print('\nlist books paginated...\n')
print('\n\n' + repr(ll.books_list(isbn='10000', page=0, size=2)) + '\n')

print('\nlist free...\n')
print('\n\n' + repr(ll.books_status('10000')) + '\n')

print('\nborrowing book...\n')
print('\n\n' + repr(ll.borrow_book(1337, 8832893)) + '\n')

print('\nlist free...\n')
print('\n\n' + repr(ll.books_status('10000')) + '\n')

print('\nreturning book...\n')
print('\n\n' + repr(ll.return_book(1337)) + '\n')

print('\nremoving test book...\n')
print('\n\n' + repr(ll.delete_book(1337)) + '\n')
print('\n\n' + repr(ll.delete_book(1338)) + '\n')
print('\n\n' + repr(ll.delete_book(1339)) + '\n')

print('\nlist books...\n')
print('\n\n' + repr(ll.books_list()) + '\n')

print('\nadding nonsence isbn...\n')
print('\n\n' + repr(ll.add_book(1230323832, 'asldjs12')) + '\n')