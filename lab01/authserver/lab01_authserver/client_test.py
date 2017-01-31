#!/usr/bin/python3

from lab01_authserver_app.oauthclient import *
import json
import requests
import time


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
print('\n\n' + repr(client.verify()) + '\n')
tokens = client.issue_tokens()
print('\n\n' + repr(tokens) + '\n')
tp = TokenPlugin(atoken = tokens['access_token'], rtoken = tokens['refresh_token'])
client.auth_plugin = tp
print('\n\n' + repr(client.verify()) + '\n')
time.sleep(5)
print('\n\n' + repr(client.verify()) + '\n')
