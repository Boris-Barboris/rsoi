from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden, \
    HttpResponseRedirect, HttpResponseBadRequest

import logging
log = logging.getLogger('client_app')

# Create your views here.

from .oauthclient import *

OAUTH_URL = 'http://192.168.243.5:39000'  # ой всё, ни слова про DNS
CLIENT_ID = 'test_client_lab01'
CLIENT_URL = 'http://192.168.243.5:39001'

def index(request):
    log_request(request)
    if request.method == 'GET':
        # check if we have code in parameters
        code = request.GET.get('code', None)
        if code:
            # get token
            gp = GrantPlugin(code)
            client = OAuthClient(OAUTH_URL, gp, CLIENT_ID, 'clientsecret', CLIENT_URL)
            try:
                tclient = client.make_token_client()
            except ExpiredException as ee:
                tokens = str(ee)
                verify_status = 'None, auth_code expired!'
            else:
                tokens = tclient.auth_plugin.token_raw
                try:
                    verify_status = tclient.verify()
                except ExpiredException as ee:
                    verify_status = str(ee)
            # let's render template            
            response = render(request, 'index.html', 
                {'grant':           code,
                 'tokens':          tokens,
                 'verify_status':   verify_status,
                })
        else:
            # let's redirect for authorization
            data = {}
            data['response_type'] = 'code'
            data['client_id'] = CLIENT_ID
            data['redirect_uri'] = CLIENT_URL
            redirect_uri = OAUTH_URL + '/auth' + query_string(data)
            response = HttpResponseRedirect(redirect_uri)
    # first check if we have auth_grant in request
    else:
        response = HttpResponseBadRequest('400 Malformed request.')
    log.debug('response:\n' + str(response.serialize()))
    return response
    
    
def rdict(request):
    if request.method == 'GET':
        return request.GET
    elif request.method == 'POST':
        return request.POST
    return None
    
def log_request(request):
    log.debug(str(request))
    log.debug('GET: ' + str(request.GET))
    log.debug('POST: ' + str(request.POST))
    log.debug('Cookies:\n' + repr(request.COOKIES))
    
def query_string(params):
    str = '?'
    for k in params:
        if len(str) > 1:
            str = str + '&'
        str = str + k + '=' + params[k]
    return str