#!/usr/bin/python3

from app_local_library.oauthclient import *
from app_local_library.local_library_client import *
import json


pp = PasswordPlugin('admin', 'admin')
client = OAuthClient('http://127.0.0.1:39000', pp, 'debug_client', 'mysecret', 'localhost')
print('\nVerification using password plugin\n')
print('\n\n' + repr(client.verify()) + '\n')
print('\nissuing tokens...\n')
tokens = client.get_token()
print('\n\ntoken:\n')
print('\n' + repr(tokens) + '\n')

ll = LocalLibClient('http://localhost:39002', client)

print('\nlist books...\n')
print('\n\n' + repr(ll.books_list()) + '\n')

test_population = [
    {'id': 1,
     'isbn': 10000,
    },
    {'id': 2,
     'isbn': 10000,
    },
    {'id': 3,
     'isbn': 10000,
    },
    {'id': 4,
     'isbn': 10001,
    },
    {'id': 5,
     'isbn': 10001,
    },
    {'id': 6,
     'isbn': 10002,
    },
    {'id': 7,
     'isbn': 10003,
    },
    ]

print('\nadding test books...\n')
i = 10000
for p in test_population:
    try:
        print('\n\n' + repr(ll.add_book(**p)) + '\n')
    except Exception as e:
        print(repr(e))
    i += 1

print('\nlist books...\n')
print('\n\n' + repr(ll.books_list()) + '\n')

print('\nlist books filtered...\n')
print('\n\n' + repr(ll.books_list(isbn=10000)) + '\n')