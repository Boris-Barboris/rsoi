#!/usr/bin/python3

from app_book_registry.oauthclient import *
from app_book_registry.book_registry_client import *
import json


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

test_population = [
    {
        'title': 'Война и Мир (том 1)',
        'authors': 'Толстой Л.Н.',
        'page_count': 300,
        'year': 1865,
    },
    {
        'title': 'Война и Мир (том 2)',
        'authors': 'Толстой Л.Н.',
        'page_count': 290,
        'year': 1867,
    },
    {
        'title': 'Война и Мир (том 3)',
        'authors': 'Толстой Л.Н.',
        'page_count': 310,
        'year': 1869,
    },
    {
        'title': 'Методы Оптимизации',
        'authors': 'Аттетков А.В., Галкин С.В., Зарубин В.С.',
        'page_count': 433,
        'year': 2001,
    },
    ]

print('\nadding test prints...\n')
i = 10000
for p in test_population:
    try:
        print('\n\n' + repr(ll.add_print(str(i), p)) + '\n')
    except Exception as e:
        print(repr(e))
    i += 1

print('\nlist prints...\n')
print('\n\n' + repr(ll.list_prints()) + '\n')

print('\nlist prints filtered...\n')
print('\n\n' + repr(ll.list_prints(title='оптимизации')) + '\n')