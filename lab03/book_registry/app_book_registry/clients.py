import json
import logging
import re
import traceback

from django.conf import settings
from .oauthclient import *

from .local_library_client import LocalLibClient
from .book_registry_client import BookRegistryClient

def oauth_client_grant(grant, redirect):
    auth_url = 'http://' + settings.AUTH_SERVER
    gp = GrantPlugin(grant_code=grant)
    ac = OAuthClient(auth_url, gp, settings.CLIENT_ID,
            settings.SECRET_KEY, redirect)
    return ac

def oauth_client(token, rtoken=None):
    auth_url = 'http://' + settings.AUTH_SERVER
    tp = TokenPlugin(atoken=token, rtoken=rtoken)
    ac = OAuthClient(auth_url, tp, settings.CLIENT_ID,
            settings.SECRET_KEY, 'localhost')    
    return ac
        
# client factories
def local_library_client(token, ac = None):
    if not ac:
        ac = oauth_client(token)
    ll = LocalLibClient('http://' + settings.LOCAL_LIB, ac)
    return ll
    
def book_registry_client(token, ac = None):
    if not ac:
        ac = oauth_client(token)
    br = BookRegistryClient('http://' + settings.BOOK_REGISTRY, ac)
    return br