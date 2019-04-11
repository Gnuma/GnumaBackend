'''
Migration N 17:

- Chat model has been defined.
- Message model has been defined.

* delete this comment
'''
from django.db import models
from gnuma.models import GnumaUser, Ad

class Chat(models.Model):
    '''
    For now, CASCADE action is used by the item's foreign key. In future, it will modified to SET NULL in order
    to enable Quipu to issue a notification any time a seller delete an item.
    '''
    item = models.ForeignKey(Item, on_delete = models.CASCADE, on_update = models.CASCADE)
    buyer = models.ForeignKey(GnumaUser, on_delete = models.CASCADE, on_update = models.CASCADE)
    created = models.DateTimeField(auto_now = True)
    '''
    Group name used by channels. 
    It is randomly generated.

    MAX 5 CHARACTERS
    '''
    group = models.CharField(unique = True, max_length = 5)
    STATUS = {
        (PENDING, 0),
        (PROGRESS, 1),
        (EXCHANGE, 2),
        (FEEDBACK, 3),
        (COMPLETED, 4)
    }
    status = models.IntegerField(choices = STATUS, default = PENDING, blank = True)

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete = models.CASCADE, on_update = models.CASCADE)
    content = models.CharField(max_length = 255)
    created = models.DateTimeField(auto_now = True)
