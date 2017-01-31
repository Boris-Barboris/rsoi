from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from lab01_authserver_app.auth import login_controller, users_controller, \
    log_request, auth_controller, token_controller_issue, \
    token_controller_verify, token_controller_refresh, token_controller_grant, \
    users_controller_me, users_controller_list


def auth(request):
    return auth_controller(request)
    
def login(request):
    return login_controller(request)
    
def users(request):
    return users_controller(request)
    
def users_me(request):
    if request.method == 'GET':
        return users_controller_me(request)
    return HttpResponse('400 Malformed request.', status = 400)
    
def users_list(request):
    if request.method == 'GET':
        return users_controller_list(request)
        return HttpResponse('400 Malformed request.', status = 400)
    
def token_issue(request):
    if request.method == 'POST':
        return token_controller_issue(request)
    return HttpResponse('400 Malformed request.', status = 400)
    
def token_verify(request):
    if request.method == 'POST':
        return token_controller_verify(request)
    return HttpResponse('400 Malformed request.', status = 400)
    
def token_refresh(request):
    if request.method == 'POST':
        return token_controller_refresh(request)
    return HttpResponse('400 Malformed request.', status = 400)
    
def token_grant(request):
    if request.method == 'POST':
        return token_controller_grant(request)
    return HttpResponse('400 Malformed request.', status = 400)