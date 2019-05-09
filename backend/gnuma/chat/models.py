'''
Migration N 17:

- Chat model has been defined.
- Message model has been defined.

Migration N 20:

- default pk field replaced with '_id' field.
- 'created' field turns into 'createdAt'
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
    _id = models.AutoField(primary_key = True)
    item = models.ForeignKey(Ad, on_delete = models.CASCADE, related_name = 'chats')

    #
    # GnumaUser is not useful at all. 
    # I should consider to replace it with a simple User instance.
    #
    buyer = models.ForeignKey(GnumaUser, on_delete = models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add = True)
    LOCAL = 0
    PENDING = 1
    PROGRESS = 2 
    EXCHANGE = 3
    FEEDBACK = 4
    COMPLETED = 5
    REJECTED = 6
    STATUS = {
        (LOCAL, 'Local chat'),
        (PENDING, 'Chat pending'),
        (PROGRESS, 'In progress chat'),
        (EXCHANGE, 'In exchange chat'),
        (FEEDBACK, 'Feedback chat'),
        (COMPLETED, 'Chat completed'),
        (REJECTED, 'Chat rejected')
    }
    status = models.IntegerField(blank = True, choices = STATUS, default = LOCAL)

class Message(models.Model):
    _id = models.AutoField(primary_key = True)
    user = models.ForeignKey(GnumaUser, on_delete = models.CASCADE, blank = True, null = True)
    chat = models.ForeignKey(Chat, on_delete = models.CASCADE, to_field = '_id' ,related_name = 'messages')
    text = models.CharField(max_length = 255)
    is_read = models.BooleanField()
    createdAt = models.DateTimeField(auto_now_add = True)
    system = models.BooleanField(blank = True, default = False)

class Client(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    channel_name = models.TextField(max_length = 100)

    def __str__(self):
        return self.user.__str__()+"  "+self.channel_name

class Notification(models.Model):
    _id = models.AutoField(primary_key = True)
    destination = models.ForeignKey(User, on_delete = models.CASCADE)
    item = models.ForeignKey(Ad, on_delete = models.CASCADE)
    notification = models.TextField(max_length = 500)
    createdAt = models.DateTimeField(auto_now_add = True)
    #
    # Allowed types.
    #
    TYPES = [
        'newComment',
        'newAnswer'
    ]

    def __str__(self):
        return self.notification

class Offert(models.Model):
    offert = models.FloatField()
    is_buyer = models.BooleanField()
    chat = models.ForeignKey(Chat, on_delete = True, related_name = 'offerts')
    PENDING = 0
    ACCEPTED = 1
    REJECTED = 2
    STATUS = {
        (PENDING, 'Pending offert'),
        (ACCEPTED, 'Offert accepted'),
        (REJECTED, 'Offert rejected')
    }
    status = models.IntegerField(blank = True, choices = STATUS, default = PENDING)
    createdAt = models.DateTimeField(auto_now_add = True)

