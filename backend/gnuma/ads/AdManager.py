# OS imports
import os, sys

# Django imports
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

# Rest imports
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, action, parser_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import  IsAuthenticated , AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser

# local imports
from gnuma.models import GnumaUser, Book, Office, Class, Ad, Queue_ads, ImageAd
from gnuma.serializers import BookSerializer, AdSerializer, QueueAdsSerializer
from .imageh import ImageHandler
from gnuma.doubleCheck.doubleCheckLayer import DoubleCheck
from gnuma.users_profiling.itemAccess import BaseProfiling
from gnuma.chat.notification import NotificationHandler

"""
The following class contains all the endpoint that are meant to handle the following actions:

- Create item.
- Enqueue item.
- Retrieve item.
- Search items.
"""
class AdManager(viewsets.GenericViewSet):
    authentication_classes = [TokenAuthentication]
    safe_actions = ('list', 'retrieve','search','geo_search')
    queryset = Ad.objects.all()
    serializer_class = AdSerializer


    def get_permissions(self):
        if self.action in self.safe_actions:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated] 
        return [permission() for permission in permission_classes]
        

    '''
    The following method cannot be called directly. It's used by the create endpoint whenever it found a mismatch
    beetwen the request's information and the db's. It basically allows Quipu to have a basic content-control system.

    V2: This endpoint supports image uploading via multipart/form-data
    '''


    def enqueue(self, request):
        user = GnumaUser.objects.get(user = request.user)

        instance = {'description': request.data['description'], 'price': request.data['price'], 'seller': user, 'enabled': False, 'condition' : request.data['condition']}
        if not self.get_serializer_class()(data = instance).is_valid():
            return JsonResponse({'detail' : 'bad format!'}, status = status.HTTP_400_BAD_REQUEST)
        enqueued = Ad.objects.create(**instance)
        instance = {'ad': enqueued, 'book_title': request.data['book_title'], 'isbn': request.data['isbn']}
        try:
            QueueAdsSerializer(data = instance).is_valid(raise_exception = True)
        except (ValidationError, TypeError) as e:
            print(str(e))
            return JsonResponse({'detail':'data is not valid!'}, status = status.HTTP_400_BAD_REQUEST)
        e = Queue_ads.objects.create(**instance)  
        e.save()

        images = {}
        result = []

        if request.data['0']:
            '''
            The request has at least one image attached.
            '''
            images['0'] = request.data['0']
            i = 1
            while str(i) in request.data:
                images[str(i)] = request.data[str(i)]
                i += 1
            content_type = request.META['CONTENT_TYPE']
            image = ImageHandler(content = images, content_type = content_type)
            result = image.open()
            #
            # result variable is an ImageAd's array containing the images.
            #
            for image in result:
                image.ad = e
                image.save()

        enqueued.save()
        user.adsCreated = user.adsCreated+1
        user.save()
        
        return JsonResponse({'detail':'item enqueued!'}, status = status.HTTP_201_CREATED)



    '''
    The following method creates an item.

    The client should indicate whether the book has been selected from the hints.
    If it wasn't the client should add 'book_title' into the JSON object.
    Each request that has the 'book_title' creates an enqueued item, that eventually will be enabled by the staff.   
    
    V2 : This method supports image uploading via multipart/form-data.
    '''
    def create(self, request):
        user = GnumaUser.objects.get(user = request.user)
        if not DoubleCheck(token = request.auth).is_valid():
            return JsonResponse({'detail' : 'your token has expired'}, status = status.HTTP_401_UNAUTHORIZED)


        if user.level == "Free" and user.adsCreated == 10:
            return JsonResponse({'detail':'The user cannot insert any other item!'}, status = status.HTTP_403_FORBIDDEN)
        elif user.level == "Pro" and user.adsCreated == 20:
            return JsonResponse({'detail':'The user cannot insert any other item!'}, status = status.HTTP_403_FORBIDDEN)
        
        # Check the arguments' validity
        if 'description' not in request.data or 'price' not in request.data or 'isbn' not in request.data or 'condition' not in request.data:
            return JsonResponse({"detail":"one or more arguments are missing!"}, status = status.HTTP_400_BAD_REQUEST)

        if 'book_title' in request.data:
            return self.enqueue(request)
        
        try: 
            book = Book.objects.get(isbn = request.data['isbn'])
        except Book.DoesNotExist:
            return JsonResponse({'detail':'the book does not exist'}, status = status.HTTP_400_BAD_REQUEST)

        instance = {'description': request.data['description'], 'price': request.data['price'], 'book': book, 'seller': user, 'condition' : request.data['condition']}

        try: 
            self.get_serializer_class()(data = instance).is_valid(raise_exception = True)
        except ValidationError as e:
            print(str(e))
            return JsonResponse({'detail':'data is not valid!'}, status = status.HTTP_400_BAD_REQUEST)
        except TypeError as e:
            print(str(e))
            return JsonResponse({'detail':'the server was not able to process your request!'}, status = status.HTTP_400_BAD_REQUEST)
       
        try:
            Ad.objects.get(book = book, seller = user)
            return JsonResponse({'detail':'item already exists!'}, status = status.HTTP_409_CONFLICT)
        except Ad.DoesNotExist:
            newAd = Ad.objects.create(**instance)
        newAd.save()
        
        images = {}
        result = []
        if request.data['0']:
            '''
            The request has at least one image attached.
            '''
            images['0'] = request.data['0']
            i = 1
            while str(i) in request.data:
                images[str(i)] = request.data[str(i)]
                i += 1
            content_type = request.META['CONTENT_TYPE']
            image = ImageHandler(content = images, content_type = content_type)
            result = image.open()
            #
            # result variable is an ImageAd's array containing the images.
            #
            for image in result:
                image.ad = newAd
                image.save()

        user.adsCreated = user.adsCreated+1
        user.save()

        #
        # Profiling
        #
        instance = {'item' : newAd, 'user' : request.user}
        try:
            BaseProfiling.createAccess(**instance)
        except Exception as e:
            print(str(e))
            return JsonResponse({'detail' : 'something went wrong!'}, status = status.HTTP_400_BAD_REQUEST)

        return JsonResponse({'detail' : 'item created!'}, status = status.HTTP_201_CREATED)


    def retrieve(self, request, *args, **kwargs):
        ad = self.get_object()

        if type(request.user) != AnonymousUser:
            #
            #   If the user is authenticated, register this access.
            #
            instance = {'item' : ad, 'user' : request.user}
            if not BaseProfiling.update(**instance):
                BaseProfiling.createAccess(**instance)

        serializer = self.get_serializer_class()(ad, many = False, context = {'request': request})
        #
        # Delete all the notification related to this user and this item.
        #
        if request.user != AnonymousUser:
            if not NotificationHandler.delete(item = ad, user = request.user):
                print('ERROR ON RETRIEVE: %d - THE NOTIFICATION HAS NOT BEEN DELETED FROM THE DATABASE' & ad.pk)
        return JsonResponse(serializer.data, status = status.HTTP_200_OK, safe = False)


    @action(detail = False, methods = ['post'])
    def search(self, request):
        #
        # The first step attempts to determine whether the user has chosen one of the hints or not.
        # If the POST request contains an 'isbn' key, it means the user has effectively chosen one hints,
        # and then this view just returns the items related to the book with that isbn.
        # If the request does not contain the 'isbn' key, then this just tries to figure out what the user
        # may be looking for.
        #
        # This view returns items grouped by offices.
        #

        if 'isbn' not in request.data and 'keyword' not in request.data:
            return JsonResponse({'detail':'one or more argument are missing!'}, status = status.HTTP_400_BAD_REQUEST)
        
        if 'isbn' in request.data and 'keyword' in request.data:
            return JsonResponse({'detail':'ambiguous arguments!'}, status = status.HTTP_400_BAD_REQUEST) 
        
        if 'isbn' in request.data:
            #
            # The user has chosen the book from the hints.
            #
            response = {}
            isbn = request.data['isbn']
            ads = Ad.objects.filter(book__pk = isbn)
            #
            # Sorting function
            #
            results = self.get_serializer_class()(ads, many = True, context = {'request' : request})
            response['resultType'] = 'single'      
            response['results'] = results.data

            return JsonResponse(response, status = status.HTTP_200_OK, safe = False)
        else:
            return JsonResponse({'detail':'this function is not implemented!'}, status = status.HTTP_400_BAD_REQUEST)
