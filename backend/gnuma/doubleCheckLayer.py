# OS imports
from datetime import datetime, timedelta, timezone

# Django imports
from django.contrib.auth.models import User

# Rest imports
from rest_framework.authtoken.models import Token

'''

Base class of the double-check layer.

'''

class DoubleCheck:

    def __init__(self, **kwargs):
        if 'token' not in kwargs:
            return None

        self.token = kwargs['token']

    '''

    Gets token object.

    '''
    def getToken(self):
        try: 
            t = Token.objects.get( key = self.token ) 
            return t
        except Token.DoesNotExist:
            return False

    '''
    
    Checks whether the token is related to an administrator.

    '''

    def is_admin(self):  
        t = self.getToken()
        if not t:
            return False
        user = User.objects.get(username = t.user)
        if user.is_staff or user.is_superuser:
            return True
        else:
            return False

    '''

    Checks the token's validity.

    If the token has expired, it returns false;
    otherwise it returns true.

    '''
    def is_valid(self): 
        if self.is_admin():
            return True
        t = self.getToken()
        if not t:
            return False
        now = datetime.now(timezone.utc)
        difference = (now - t.created).total_seconds()
        if difference >= 7200:
            return False
        else:
            return True
        
        

        