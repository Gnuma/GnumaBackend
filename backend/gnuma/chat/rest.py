# global imports
import uuid # deprecated

# Django imports
from django.http import JsonResponse
from django.db.models import Max

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
from .serializers import CreateChatSerializer, ChatSerializer, NotificationMessageSerializer, NotificationChatSerializer, RetrieveAdSerializer
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
        if buyer == item.seller:
            return JsonResponse({'detail' : 'you cannot create a chat with yourself'}, status  = status.HTTP_409_CONFLICT)
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
            #
            pass
        #
        # Return chat informations
        #

        return JsonResponse(CreateChatSerializer(chat, many = False, context = {'request' : request}), status = status.HTTP_201_CREATED, safe = False) 

    @action(detail = False, methods = ['post'])
    def confirmChat(self, request):
        if 'chat ' not in request.data:
            return JsonResponse({'detail' : 'one or more arguments are missing!'}, status = status.HTTP_400_BAD_REQUEST)
        
        try:
            chat = Chat.objects.get(pk = request.data['chat'])
        except Chat.DoesNotExist:
             return JsonResponse({'detail' : 'the chat does not exist!'}, status = status.HTTP_400_BAD_REQUEST)
        
        chat.status = Chat.PENDING
        chat.save()

        return JsonResponse({'status' : 'chat confirmed!'}, status = status.HTTP_200_OK)

    '''
    This endpoint changes the status of the given chat from 'pending' to 'progress'.

    Parameters:

    - chatID (chat)
    '''
    @action(detail = False, methods = ['post'])
    def accept(self, request):
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
    @action(detail = False, methods = ['post'])
    def reject(self, request):
        if 'chat' not in request.data:
            return JsonResponse({'detail' : 'one or more arguments are missing!'}, status = status.HTTP_400_BAD_REQUEST)
        
        try:
            chat = Chat.objects.get(pk = request.data['chat'])
        except Chat.DoesNotExist:
            return JsonResponse({'detail' : 'the chat does not exist!'}, status = status.HTTP_400_BAD_REQUEST)
        
        #
        # rejected not delete.
        #
        chat.status = Chat.REJECTED
        chat.save()
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
class ChatsOperations(viewsets.GenericViewSet):
    queryset = Chat.objects.all()
    authentication_classes = [TokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    '''
    This endpoint is called every time the user turns from inactive to active.
    It must return all the user's chats splitted in 'sales' and 'shoping'.
    Also, each chat must return together with its last 50 messages.
    '''
    def list(self, request):
        response = {}
        #
        # Sales
        #
        response['sales'] = []
        null_ads = Ad.objects.filter(chats__isnull = True, seller__user = request.user).order_by('-createdAt')
        chat_ads = Ad.objects.annotate(max = Max('chats__messages__createdAt')).filter(chats__isnull = False, seller__user = request.user).order_by('pk').order_by('-max')
        for ad in chat_ads:
            response['sales'].append(RetrieveAdSerializer(ad, many = False, context = {'request' : request}).data)
        for ad in null_ads:
            response['sales'].append(RetrieveAdSerializer(ad, many = False, context = {'request' : request}).data)
        #
        # Shopping
        #
        response['shopping'] = []
        chat_ads = Ad.objects.annotate(max = Max('chats__messages__createdAt')).filter(chats__isnull = False, chats__buyer__user = request.user).order_by('pk').order_by('-max')
        ordered_subjects = []
        for ad in chat_ads:
            if ad.book.subject not in ordered_subjects:
                ordered_subjects.append(ad.book.subject)
        for subject in ordered_subjects:
            data = {}
            data['subject'] = {'_id' : subject._id, 'title' : subject.title}
            data['items'] = []
            ads = Ad.objects.annotate(max = Max('chats__messages__createdAt')).filter(chats__isnull = False, chats__buyer__user = request.user, book__subject = subject).order_by('pk').order_by('-max')
            for ad in ads:
                data['items'].append(RetrieveAdSerializer(ad, many = False, context = {'user' : request.user, 'request' : request}).data)
            response['shopping'].append(data)
        return JsonResponse(response, status = status.HTTP_200_OK, safe = False)
    '''
    This endpoint is used by the user in order to push a message into a chat.

    Parameters:

    - chatID (chat)
    - content
    '''
    def create(self, request):
        if 'chat' not in request.data or 'content' not in request.data:
            return JsonResponse({'detail' : 'one or more arguments are missing!'}, status = status.HTTP_400_BAD_REQUEST)

        try:
            chat = Chat.objects.get(pk = request.data['chat'])
        except Chat.DoesNotExist:
            return JsonResponse({'detail' : 'the chat does not exist!'}, status = status.HTTP_400_BAD_REQUEST)

        if chat.item.seller.user != request.user and chat.buyer.user != request.user:
            return JsonResponse({'detail' : 'you cannot send messages in this chat!'}, status = status.HTTP_401_UNAUTHORIZED)

        instance = {'chat' : chat, 'user' : GnumaUser.objects.get(user = request.user), 'text' : request.data['content'], 'is_read' : False}
        serializer = NotificationMessageSerializer(data = instance)
        try:
            serializer.is_valid(raise_exception = True)
        except Exception as e:
            print('SEND MESSAGE - ERROR DETECTED : %s' % str(e))
            return JsonResponse({'detail' : 'data entered is not valid'}, status = status.HTTP_400_BAD_REQUEST)
        
        message = Message.objects.create(**instance)
        message.save()
        #
        # Notification must be sent to the other user.
        #
        item = chat.item
        data = {}
        data['type'] = "NewMessage"
        if item.seller.user == request.user:
            #
            # I'm the seller
            #
            destination = chat.buyer.user
            data['for'] = "shopping"
            data['objectID'] = item.book.subject.pk
        else:
            destination = item.seller.user
            data['for'] = "sale"
            data['objectID'] = item.pk
        data['chatID'] = chat.pk
        data['message'] = NotificationMessageSerializer(message, many = False).data
        try:
            client = Client.objects.get(user = destination)
            channel_name = client.channel_name
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.send)(channel_name, {"type" : "notification.send", "content" : data})
        except Client.DoesNotExist:
            pass

        return JsonResponse({'pk' : message.pk}, status = status.HTTP_201_CREATED)