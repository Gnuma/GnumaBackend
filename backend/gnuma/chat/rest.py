# global imports
import uuid

# Django imports
from django.http import JsonResponse

# Rest imports
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import  IsAuthenticated , AllowAny
from rest_framework.decorators import action

# local imports
from .models import Chat, Message
from .serializers import ChatSerializer
from gnuma.models import Ad, GnumaUser

class ChatsEndpoints(viewsets.GenericViewSet):
    queryset = Chat.objects.all()
    authentication_classes = [TokenAuthentication, ]
    safe_actions = ['retrieve']

    def get_permissions(self):
    if self.action in self.safe_actions:
        permission_classes = [AllowAny, ]
    else:
        permission_classes = [IsAuthenticated, ]

    return [permission() for permission in permission_classes]

    def createChat(self, request):
        if 'item' not in request.data:
            return JsonResponse({'detail' : 'one or more arguments are missing!'}, status = status.HTTP_400_BAD_REQUEST)
        
        try:
            item = Ad.objects.get(pk = request.data['item'])
        except Ad.DoesNotExist:
            return JsonResponse({'detail' : 'the item does not exist!'}, status = status.HTTP_400_BAD_REQUEST)
        
        buyer = GnumaUser.objects.get(user = request.user)
        instance = {'buyer' : buyer, 'item' : item, 'group' : str(uuid.uuid4()[:5])}
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

        serializer.save()
        return JsonResponse({'detail' : 'chat created!'}, status = status.HTTP_201_CREATED) 

