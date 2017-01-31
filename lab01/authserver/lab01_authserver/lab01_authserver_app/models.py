from django.db import models
import hashlib
import uuid
from datetime import datetime
from django.utils import timezone

salt = 'authsecretkey'

atoken_lifetime = 4
rtoken_lifetime = 3600
agcode_lifetime = 4

# Create your models here.

class User(models.Model):
    uname = models.CharField(max_length=100, primary_key=True)
    password_hash = models.CharField(max_length=200)
    def __str__(self):
        return '<User: uname = ' + self.uname + '>'
    
class AccessToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=200, primary_key = True)
    client_id = models.CharField(max_length=200, null = True)
    issued = models.DateTimeField('date issued')
    def __str__(self):
        return '<AccessToken: uname = ' + user.uname + '; ' + \
            'token = ' + self.token + '; issued = ' + str(self.issued) + '>'
            
class RefreshToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rtoken = models.CharField(max_length=200, primary_key = True)
    client_id = models.CharField(max_length=200, null = True)
    issued = models.DateTimeField('date issued')
    def __str__(self):
        return '<RefreshToken: uname = ' + user.uname + '; ' + \
            'rtoken = ' + self.rtoken + '; issued = ' + str(self.issued) + '>'
    
class AuthGrantCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=200, primary_key = True)
    issued = models.DateTimeField('date issued')
    def __str__(self):
        return '<AuthGrantCode: uname = ' + user.uname + '; ' + \
            'code = ' + self.code + '; issued = ' + str(self.issued) + '>'
            

# exceptions
            
class AccessTokenExpired(Exception):
    def __init__(self, token):
        Exception.__init__(self, 'Access token ' + token + ' expired')
        self.token = token
        
class RefreshTokenExpired(Exception):
    def __init__(self, token):
        Exception.__init__(self, 'Refresh token ' + token + ' expired')
        self.token = token
        
class AuthGrantCodeExpired(Exception):
    def __init__(self, code):
        Exception.__init__(self, 'Auth code ' + code + ' expired')
        self.code = code
            
# model operations

def authenticate(uname, password):
    try:
        hashed_password = hashlib.sha512(password.encode('utf-8') + 
            salt.encode('utf-8')).hexdigest()
    except:
        return None
    try:
        dbuser = User.objects.get(pk = uname)
    except User.DoesNotExist:
        return None
    if dbuser.password_hash == hashed_password:
        return dbuser
    else:
        return None
        
def authenticate_token(access_token):
    try:
        token = AccessToken.objects.get(pk = access_token)
        if (timezone.now() - token.issued).total_seconds() > atoken_lifetime:
            raise AccessTokenExpired(token.token)
        user = token.user
        return user
    except AccessToken.DoesNotExist:
        return None
        
def authenticate_rtoken(refresh_token):
    try:
        token = RefreshToken.objects.get(pk = refresh_token)
        if (timezone.now() - token.issued).total_seconds() > rtoken_lifetime:
            raise RefreshTokenExpired(token.rtoken)
        user = token.user
        return user
    except RefreshToken.DoesNotExist:
        return None
        
def authenticate_authcode(code):
    try:
        authcode = AuthGrantCode.objects.get(pk = code)
        if (timezone.now() - authcode.issued).total_seconds() > agcode_lifetime:
            raise AuthGrantCodeExpired(authcode.code)
        user = authcode.user
        return user
    except AuthGrantCode.DoesNotExist:
        return None
        
def issue_grantcode(user):
    code = AuthGrantCode(code = uuid.uuid4().hex, user = user, 
        issued = timezone.now())
    code.save()
    return code
    
def issue_tokens(user, client_id = None):
    now = timezone.now()
    atoken = AccessToken(user = user, token = uuid.uuid4().hex, issued = now, 
        client_id = client_id)
    rtoken = RefreshToken(user = user, rtoken = uuid.uuid4().hex, issued = now, 
        client_id = client_id)
    atoken.save()
    rtoken.save()
    return {'atoken': atoken, 'rtoken': rtoken}
    
        
def register_user(uname, password):
    if len(uname) > 0 and len(password) > 0:
        try:
            if User.objects.get(pk = uname):
                raise Exception('User already exists')
        except User.DoesNotExist:
            pass
        hashed_password = hashlib.sha512(password.encode('utf-8') + 
            salt.encode('utf-8')).hexdigest()
        user = User(uname = uname, password_hash = hashed_password)
        user.save()
        return user
    else:
        raise Exception('Bad login or password')
        
def list_users():
    return User.objects.all()
    
def delete_user(uname):
    dbuser = User.objects.get(pk = uname)
    dbuser.delete()