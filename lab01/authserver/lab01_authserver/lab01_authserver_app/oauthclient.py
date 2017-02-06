import json
import requests


OAUTH_OK = 0
OAUTH_EXPIRED = 1


class UnauthorizedException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
        
class ForbiddenException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

class ExpiredException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
        
class AuthResponseException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class PasswordPlugin():
    def __init__(self, uname, password):
        self.uname = uname
        self.password = password
        
    def verify(self, auth_url, s):
        r = s.get(auth_url + '/users/me', 
            cookies = {'uname': self.uname, 'password': self.password })
        if r.status_code == 200:
            return OAUTH_OK
        else:
            raise AuthResponseException('Response = ' + repr(r.status_code))
            
    def me(self, auth_url, s):
        r = s.get(auth_url + '/users/me', 
            cookies = {'uname': self.uname, 'password': self.password })
        if r.status_code == 200:
            return json.loads(r.text)
        elif r.status_code == 401:
            raise UnauthorizedException('401 Unauthorized')
        else:
            raise AuthResponseException('Response = ' + repr(r.status_code))
            
    def issue_tokens(self, auth_url, s, client_id, client_secret, redirect_uri):
        data = {'uname': self.uname, 'password': self.password }
        r = s.post(auth_url + '/token/grant', data = data)
        if r.status_code == 200:
            code = r.text
        elif r.status_code == 401:
            raise UnauthorizedException('401 Unauthorized')
        else:
            raise AuthResponseException('Response = ' + repr(r.status_code))
        grant_plugin = GrantPlugin(code)
        client = OAuthClient(auth_url, grant_plugin, client_id, client_secret, 
            redirect_uri)
        return client.issue_tokens()
        
        
class GrantPlugin():
    def __init__(self, grant_code):
        self.code = grant_code
        
    def verify(self, auth_url, s):
        raise NotImplementedError()
        
    def me(self, auth_url, s):
        raise NotImplementedError()
        
    def issue_tokens(self, auth_url, s, client_id, client_secret, redirect_uri):
        data = {'grant_type':       'authorization_code',
                'client_id':        client_id,
                'client_secret':    client_secret,
                'redirect_uri':     redirect_uri,
                'code':             self.code}
        r = s.post(auth_url + '/token/issue', data = data)
        if r.status_code == 200:
            # form dict from json
            tokens = json.loads(r.text)
            return tokens
        elif r.status_code == 401:
            raise UnauthorizedException('401 Unauthorized')
        elif r.status_code == 440:
            raise ExpiredException('Grant code ' + self.code + ' expired')
        else:
            raise AuthResponseException('Response = ' + repr(r.status_code))
        
        
class TokenPlugin():
    def __init__(self, atoken, rtoken):
        self.atoken = atoken
        self.rtoken = rtoken
        
    def verify(self, auth_url, s):
        data = {'access_token': self.atoken}
        r = s.post(auth_url + '/token/verify', data = data)
        if r.status_code == 200:
            return OAUTH_OK
        elif r.status_code == 401:
            raise UnauthorizedException('401 Unauthorized')
        elif r.status_code == 440:
            raise ExpiredException('Access token ' + self.atoken + ' expired')
        else:
            raise AuthResponseException('Response = ' + repr(r.status_code))
            
    def me(self, auth_url, s):
        headers = {'ACCESSTOKEN': self.atoken}
        r = s.get(auth_url + '/users/me', headers = headers)
        if r.status_code == 200:
            return json.loads(r.text)
        elif r.status_code == 401:
            raise UnauthorizedException('401 Unauthorized')
        elif r.status_code == 440:
            raise ExpiredException('Access token ' + self.atoken + ' expired')
        else:
            raise AuthResponseException('Response = ' + repr(r.status_code))
            
    def issue_tokens(self, auth_url, s, client_id, client_secret, redirect_uri):
        if not self.rtoken:
            raise UnauthorizedException('Plugin has no refresh token')
        data = {'grant_type':       'refresh_token',
                'client_id':        client_id,
                'client_secret':    client_secret,
                'refresh_token':    self.rtoken}
        r = s.post(auth_url + '/token/refresh', data = data)
        if r.status_code == 200:
            # form dict from json
            tokens = json.loads(r.text)
            self.atoken = tokens['access_token']
            self.rtoken = tokens['refresh_token']
            return tokens
        elif r.status_code == 440:
            raise ExpiredException('Refresh token ' + self.rtoken + ' expired')
        else:
            raise AuthResponseException('Response = ' + repr(r.status_code))
    

class OAuthClient():
    def __init__(self, auth_url, auth_plugin, client_id, client_secret, 
            redirect_uri):
        self.session = requests.Session()
        self.auth_url = auth_url
        self.auth_plugin = auth_plugin
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
    def verify(self):
        return self.auth_plugin.verify(self.auth_url, self.session)
        
    def me(self):
        return self.auth_plugin.me(self.auth_url, self.session)
        
    def issue_tokens(self):
        tokens = self.auth_plugin.issue_tokens(self.auth_url, self.session,
            self.client_id, self.client_secret, self.redirect_uri)
        self.auth_plugin.token_raw = tokens
        return tokens
        
    def get_token(self):
        if type(self.auth_plugin) is TokenPlugin:
            return self.auth_plugin.atoken
        else:
            tokens = self.issue_tokens()
            if type(tokens) is dict:
                tp = TokenPlugin(tokens['access_token'], tokens['refresh_token'])
            self.auth_plugin = tp
            return self.auth_plugin.atoken
            
    def make_token_client(self):
        if type(self.auth_plugin) is TokenPlugin:
            return self
        else:
            tokens = self.issue_tokens()
            if type(tokens) is dict:
                tp = TokenPlugin(tokens['access_token'], tokens['refresh_token'])
                tp.token_raw = tokens
                new_client = OAuthClient(self.auth_url, tp, self.client_id,
                    self.client_secret, self.redirect_uri)
                #new_client.session = self.session
                return new_client