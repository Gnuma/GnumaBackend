'''
Migration N 17:

- Chat model has been defined.
- Message model has been defined.

* delete this comment
'''
# Django imports
from django.contrib.auth.models import User
from django.db import models

# django-mysql imports
from django_mysql.models import JSONField, Model

# local imports
from gnuma.models import GnumaUser, Ad


class Chat(models.Model):
    '''
    For now, CASCADE action is used by the item's foreign key. In future, it will modified to SET NULL in order
    to enable Quipu to issue a notification anytime a seller delete an item.
    '''
    item = models.ForeignKey(Ad, on_delete = models.CASCADE)

    #
    # GnumaUser is not useful at all. 
    # I should consider to replace it with a simple User instance.
    #
    buyer = models.ForeignKey(GnumaUser, on_delete = models.CASCADE)
    created = models.DateTimeField(auto_now_add = True)
    PENDING = 0
    PROGRESS = 1 
    EXCHANGE = 2
    FEEDBACK = 3
    COMPLETED = 4
    STATUS = {
        (PENDING, 0),
        (PROGRESS, 1),
        (EXCHANGE, 2),
        (FEEDBACK, 3),
        (COMPLETED, 4)
    }
    status = models.IntegerField(blank = True, choices = STATUS, default = PENDING)

class Message(models.Model):
    owner = models.ForeignKey(GnumaUser, on_delete = models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete = models.CASCADE, related_name = 'message_chat')
    content = models.CharField(max_length = 255)
    is_read = models.BooleanField()
    created = models.DateTimeField(auto_now_add = True)

class Client(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    channel_name = models.TextField(max_length = 100)

class Notification(models.Model):
    destination = models.ForeignKey(User, on_delete = models.CASCADE)
    notification = models.TextField(max_length = 500)
    created = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.destination.__str__()+str(self.created)

