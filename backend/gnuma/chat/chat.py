import json

# Django imports
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# channels imports
from channels.generic.websocket import WebsocketConsumer

# local imports
from .models import Client

class Chat(WebsocketConsumer):
    '''
    This method opens a new connection with the client.
    Also, it creates a new Client instance.
    '''
    def connect(self):
        if isinstance(self.scope['user'], AnonymousUser):
            print("USER NOT AUTHENTICATED")
            self.close()
        else:
            try:
                Client.objects.create(user = self.scope['user'], channel_name = self.channel_name)
            except Exception as e:
                print('ERROR OCCURED DURING THE CONNECTION WITH %s : %s' % (self.scope['user'], str(e)))
                self.close()
            self.accept()

    '''
    This method closes the connection with the client.
    Also, it deletes the Client instance.
    '''
    def disconnect(self, close_code):
        user = self.scope["user"]
        Client.objects.get(user = user).delete()

    '''
    This method will be called every time a notification must be sent to the user.
    
    Parameters:

    - event: dictionary containing the following field:
        type : notication.send
        notifcation (dict):
            message : notification's content. (see https://gist.github.com/ihategoto/59bb52900de5c0692de489d79bf66494 to know about the protocol)
    '''
    def notification_send(self, event):
        data = event["content"]
        self.send(text_data = json.dumps(data))
    
