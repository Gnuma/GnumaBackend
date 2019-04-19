# global imports
import uuid # deprecated

# Django imports
from django.http import JsonResponse

# Rest imports
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import  IsAuthenticated , AllowAny
from rest_framework.decorators import action

# Channels imports
from channels.layers import get_channel_layer

# asgiref imports
from asgiref.sync import async_to_sync

# local imports
from .models import Chat, Message, Client
from .serializers import ChatSerializer, MessageSerializer, NotificationChatSerializer
from gnuma.models import Ad, GnumaUser

'''
The following class contains all the endpoints that are meant to handle the chats' models.

It contains the following methods:

- create: create a Chat model with 'status' set to 'pending'.
- acceptChat: sets the 'status' of the given chat from 'pending' to 'progress'.
- rejectChat: delete the given chat's model.

'''
class ChatsHandling(viewsets.GenericViewSet):
    queryset = Chat.objects.all()
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    '''
    This endpoint creates a chat.
    Every chat created by this endpoint has the 'status' set to 'pending'.

    Parameters:
    - item
    '''
    def create(self, request):
        if 'item' not in request.data:
            return JsonResponse({'detail' : 'one or more arguments are missing!'}, status = status.HTTP_400_BAD_REQUEST)
        
        try:
            item = Ad.objects.get(pk = request.data['item'])
        except Ad.DoesNotExist:
            return JsonResponse({'detail' : 'the item does not exist!'}, status = status.HTTP_400_BAD_REQUEST)
        
        buyer = GnumaUser.objects.get(user = request.user)
        instance = {'buyer' : buyer, 'item' : item}
        #
        # If the chat already exists, the API return with an 409 status code
        #
        try:
            chat = Chat.objects.get(**instance)
            print('CHAT ALREADY EXISTS')
            return JsonResponse({'detail' : 'chat already exists!'}, status = status.HTTP_409_CONFLICT)
        except Chat.DoesNotExist:
            pass
        #
        # Let's create the chat.
        #
        serializer = ChatSerializer(data = instance)
        try: 
            serializer.is_valid(raise_exception = True)
        except Exception as e:
            '''
            Note that, is_valid method does raise an exception even if the uniqueness constraint fails.
            In order to prevent this problem, a more accurate check should be perfomed upon the exception.
            '''
            print('DEBUG PRINT WHILE CREATING CHAT: %s' % str(e))
            return JsonResponse({'detail' : 'data provided is not valid!'}, status = status.HTTP_400_BAD_REQUEST)

        chat = Chat.objects.create(**instance)
        chat.save()
        #
        # Issue notification to the item's owner
        #
        destination = item.seller.user
        data = {}
        data['type'] = 'newChat'
        data['chat'] = NotificationChatSerializer(chat, many = False).data
        try:
            channel_name = Client.objects.get(user = destination).channel_name
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.send)(channel_name, {"type" : "notification.send", "content" : data})
        except Client.DoesNotExist:
            #
            # The user is not online.
            # Just insert the notification into the database.
            #
            # To be implemented
            pass
        #
        # Return chat informations
        #
        return JsonResponse(data['chat'], status = status.HTTP_201_CREATED, safe = False) 

    '''
    This endpoint changes the status of the given chat from 'pending' to 'progress'.

    Parameters:

    - chatID (chat)
    '''
    def acceptChat(self, request):
        if 'chat' not in request.data:
            return JsonResponse({'detail' : 'one or more arguments are missing!'}, status = status.HTTP_400_BAD_REQUEST)
        
        try:
            chat = Chat.objects.get(pk = request.data['chat'])
        except Chat.DoesNotExist:
            return JsonResponse({'detail' : 'the chat does not exist!'}, status = status.HTTP_400_BAD_REQUEST)
        
        chat.status = Chat.PROGRESS
        chat.save()
        #
        # A notification must be sent to the buyer.
        #
        return JsonResponse(ChatSerializer(chat, many = False).data, status = status.HTTP_200_OK)

    '''
    This endpoint deletes the given chat's model.
    
    Parameters:
    
    - chatID (chat)
    '''
    def rejectChat(self, request):
        if 'chat' not in request.data:
            return JsonResponse({'detail' : 'one or more arguments are missing!'}, status = status.HTTP_400_BAD_REQUEST)
        
        try:
            chat = Chat.objects.get(pk = request.data['chat'])
        except Chat.DoesNotExist:
            return JsonResponse({'detail' : 'the chat does not exist!'}, status = status.HTTP_400_BAD_REQUEST)
        
        chat.delete()
        #
        # A notification must be sent to the buyer.
        #
        return JsonResponse({'detail' : 'chat rejected'}, status = status.HTTP_200_OK)    

    '''
    This endpoint lists all the user's pending chats.
    '''
    def retrievePendingChats(self, request):
        user = self.user
        chats = Chat.objects.filter(item__seller = user, status = Chat.PENDING)
        return JsonResponse(ChatSerializer(chats, many = True).data, status = status.HTTP_200_OK, safe = False)

'''
The following class contains all the endpoints that are meant to retrieve or push messages.

It contains the following methods:

- retrieveChat: retrieves messages from the given chat.
- sendMessage: pushes a message into the given chat.
'''
class ChatOperations(viewsets.GenericViewSet):
    queryset = Chat.objects.all()
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    '''
    This endpoint must be called every time an user is going to enter a chat.
    All the messages are going to have the flag 'is_read' set to true.
    Also, it returns the chat's messages.
    
    Parameters:

    - chatID (chat)
    - page number (page)


    '''
    def retrieveChat(self, request):
        if 'chat' not in request.data or 'page' not in request.data:
            return JsonResponse({'detail' : 'one or more arguments are missing!'}, status = status.HTTP_400_BAD_REQUEST)

        if not str.isnumeric(request.data['page']):
            return JsonResponse({'detail' : 'page number must be a number!'}, status = status.HTTP_400_BAD_REQUEST)

        try:
            chat = Chat.objects.get(pk = request.data['chat'])
        except Chat.DoesNotExist:
            return JsonResponse({'detail' : 'the chat does not exist!'}, status = status.HTTP_400_BAD_REQUEST)
        
        messages = Message.objects.filter(chat = chat, is_read = False).exclude(owner = request.data['user'])     
        
        for m in messages:
            m.is_read = True
            m.save()

        if 'live' in request.data:
            return JsonResponse({'detail' : 'chat updated'}, status = status.HTTP_200_OK)

        #
        # Retrieve chat's messages
        #       
    
        return JsonResponse(ChatSerializer(chat, many = False, context = {'page' : request.data['page']}), status = status.HTTP_200_OK, safe = False)

    '''
    This endpoint is used by the user in order to push a message into a chat.

    Parameters:

    - chatID (chat)
    - content
    '''
    def sendMessage(self, request):
        if 'chat' not in request.data or 'content' not in request.data:
            return JsonResponse({'detail' : 'one or more arguments are missing!'}, status = status.HTTP_400_BAD_REQUEST)

        try:
            chat = Chat.objects.get(pk = request.data['chat'])
        except Chat.DoesNotExist:
            return JsonResponse({'detail' : 'the chat does not exist!'}, status = status.HTTP_400_BAD_REQUEST)

        if chat.item.seller != request.user and chat.buyer != request.user:
            return JsonResponse({'detail' : 'you cannot send messages in this chat!'}, status = status.status.HTTP_401_UNAUTHORIZED)

        instance = {'chat' : chat, 'owner' : request.user, 'content' : request.data['content']}
        serializer = MessageSerializer(data = instance)
        try:
            serializer.is_valid(raise_exception = True)
        except Exception as e:
            print('SEND MESSAGE - ERROR DETECTED : %s' % str(e))
            return JsonResponse({'detail' : 'data entered is not valid'}, status = status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        #
        # Notification must be sent to the other user.
        #
        item = chat.item
        if item.seller.user == request.user:
            #
            # I'm the seller
            #
            buyer = chat.buyer
            try:
                client = Client.objects.get(user = buyer)
                channel_name = client.channel_name
                #
                # Let's create our notification
                #
                channel_layer = get_channel_layer()
                notification_content = {}
                notification_content['type'] = "NewMessage"
                notification_content['numberOfMessages'] = 1
                notification_content['messages'] = []
                notification_content['messages'].append(serializer.data.__dict__)
                notification_content['chatID'] = chat.pk
                async_to_sync(channel_layer.send(channel_name, {"type" : "notification.send", "content" : notification_content}))
            except Client.DoesNotExist:
                #
                # Save the notification
                #
                return 1
        else:
            #
            # I'm the buyer
            #
            return 1
        return JsonResponse({'detail' : 'message sent!'}, status = status.HTTP_200_OK)


