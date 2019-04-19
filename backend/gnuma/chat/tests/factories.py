from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from gnuma.chat.models import Chat
from gnuma.models import Ad, GnumaUser
import uuid
import factory 

class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username', )

class GnumaUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = GnumaUser
        django_get_or_create = ('user',)
    level = 'Free'
    adsCreated = 0

class TokenFactory(factory.DjangoModelFactory):
    class Meta:
        model = Token
        django_get_or_create = ('user', )


class ChatFactory(factory.DjangoModelFactory):
    class Meta:
        model = Chat
        django_get_or_create = ('buyer', 'item')

class ItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = Ad
        django_get_or_create = ('seller', )
    description = 'Test'
    condition = 0
    price = 10
    book = None
    enabled = True
