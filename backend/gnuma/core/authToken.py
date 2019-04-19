from channels.auth import AuthMiddlewareStack
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
import urllib

class AuthTokenMiddleware:

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        if 'query_string' not in scope:
            scope['user'] = AnonymousUser()
        else:
            query_string = urllib.parse.parse_qs(scope['query_string'])
            if b'token' not in query_string:
                scope['user'] = AnonymousUser()
            else:
                print(repr(Token.objects.all()))
                try:
                    token = Token.objects.get(key = query_string[b'token'][0].decode())
                    scope['user'] = token.user
                except Token.DoesNotExist:
                    scope['user'] = AnonymousUser()          
        return self.inner(scope)

TokenAuthMiddlewareStack = lambda inner: AuthTokenMiddleware(AuthMiddlewareStack(inner))

