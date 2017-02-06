#!/usr/bin/python3

from app_book_registry.oauthclient import *
from app_book_registry.book_registry_client import *
from app_book_registry.rsoi_common import AlreadyExists
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

ll = BookRegistryClient('http://localhost:39003', client)

print('\nlist prints...\n')
print('\n\n' + repr(ll.list_prints()) + '\n')

print('\nadding test print...\n')
test_print = {
    'title': 'TestTitle',
    'authors': 'John Bull',
    'page_count': 250,
    'year': 1967,
    }
try:
    print('\n\n' + repr(ll.add_print('38721837', test_print)) + '\n')
except AlreadyExists:
    print('\nALREADY EXISTS\n')

print('\nlist prints...\n')
print('\n\n' + repr(ll.list_prints()) + '\n')

print('\npatching test print...\n')
test_print['year'] = 1971
test_print['authors'] = 'John Bull Sr.'
print('\n\n' + repr(ll.update_print('38721837', test_print)) + '\n')

print('\nlist prints...\n')
print('\n\n' + repr(ll.list_prints()) + '\n')

print('\ndeleting test print...\n')
print('\n\n' + repr(ll.delete_print('38721837')) + '\n')

print('\nlist prints...\n')
print('\n\n' + repr(ll.list_prints()) + '\n')