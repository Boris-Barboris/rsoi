import json
import logging
import re
import traceback

from django.http import HttpResponse
from django.conf import settings
from .oauthclient import *

log = logging.getLogger('app_logging')

important_headers = (
    'HTTP_ACCESSTOKEN',
    'HTTP_ACCEPT',
    )

def request2str(r):
    str = ''
    str += r.scheme + ' path: ' + r.path + ' ' + r.method + '\n'
    str += 'GET: '
    for g in r.GET:
        str += g + ': ' + repr(r.GET[g])
    str += 'COOKIES: '
    for g in r.COOKIES:
        str += g + ': ' + repr(r.COOKIES[g])
    str += 'Headers: '
    for h in r.META:
        if h in important_headers:
            str += h + ': ' + repr(r.META[h]) + ' '
    str += 'Body: ' + repr(r.body)
    return str

def log_view(f):
    def log_request(request):
        log.debug('===Request=== ' + request2str(request))
    
    def wrap_view(request, *args, **kwargs):
        log_request(request)
        res = f(request, *args, **kwargs)
        log.debug('===Response=== ' + repr(res) + '\n' + repr(res.serialize()))
        return res
        
    return wrap_view
    
    
def _check_authorization(f, r, rexp, *args, **kwargs):
    # get authorization from request
    token = r.META.get('HTTP_ACCESSTOKEN', None)
    if token:
        # build client and verify token
        auth_url = 'http://' + settings.AUTH_SERVER
        tp = TokenPlugin(atoken=token, rtoken=None)
        client = OAuthClient(auth_url, tp, settings.CLIENT_ID,
            settings.SECRET_KEY, 'localhost')
        try:
            me = client.me()
            me['token'] = token
            log.debug('token Auth OK: ' + repr(me))
            match = rexp.match(me['uname'])
            if match:
                log.debug('uname match OK')
                return f(r, me, *args, **kwargs)
            else:
                log.debug('uname match failed')
                return HttpResponse('403 Forbidden', status=403)
        except UnauthorizedException:
            return HttpResponse('401 Unauthorized', status=401)
        except ExpiredException:
            return HttpResponse('440 Token expired', status=440)
        except Exception as e:
            log.debug('Error while verifying token: ' + traceback.format_exc())
            return HttpResponse('500 Internal Server Error', status=500)
    else:
        return HttpResponse('401 Unauthorized', status=401)    
    
def authorize_request_admin(f):
    uname_re = re.compile('^admin$')
    def _do_authorize(r, *args, **kwargs):
        return _check_authorization(f, r, uname_re, *args, **kwargs)        
    return _do_authorize
    
def authorize_request(f):
    uname_re = re.compile('.+')
    def _do_authorize(r, *args, **kwargs):
        return _check_authorization(r, uname_re, *args, **kwargs)        
    return _do_authorize
    
    
def paginate_list(l, request):
    page = request.GET.get('page', '0')
    page = int(page)
    size = request.GET.get('size', '0')
    size = int(size)
    if size > 0:
        return l[page * size : (page + 1) * size]
    else:
        return l