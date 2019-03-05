# OS imports
import os, sys

# Django imports
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.conf import settings

# Rest imports
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, action, parser_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import  IsAuthenticated , AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FileUploadParser

# Local imports
from .models import GnumaUser, Book, Office, Class, Ad, Queue_ads, ImageAd
from .serializers import BookSerializer, AdSerializer, QueueAdsSerializer
from .imageh import ImageHandler
from .doubleCheckLayer import DoubleCheck


''' 

This dict works just like a queue.
Each time a user wants to create an item he must issues two different requests:

1) The first one will upload the image onto the sever.

2) The second one will eventually relate the image, which has been previously uploaded, to the a new item.

This dict enable these two endpoints to exchange informations.                                        

'''

ImageQueue = {}

'''
init the internal user object.

#1: To be rewritten.
'''
@api_view(['POST',])
@authentication_classes([TokenAuthentication,])
def init_user(request):
    if 'key' not in request.data or 'classM' not in request.data or 'office' not in request.data:
        return JsonResponse({'detail':'one or more arguments are missing!'}, status = status.HTTP_400_BAD_REQUEST)

    try:
        token = Token.objects.get(key = request.data['key'])
    except Token.DoesNotExist:
        return JsonResponse({'detail' : 'key does not exist!'}, status = status.HTTP_400_BAD_REQUEST)

    user = User.objects.get(username = token.user)
    classM = request.data['classM'] 
    try:
        office = Office.objects.get(name = request.data['office'])
    except Office.DoesNotExist:
        return JsonResponse({'detail' : 'office does not exits!'}, status = status.HTTP_400_BAD_REQUEST)

    if len(classM) != 2:
        return JsonResponse({'detail' : 'invalid format!'}, status = status.HTTP_400_BAD_REQUEST)

    grade = classM[0]
    division = classM[1]
    try:
        c = Class.objects.get(division = division, grade = grade, office = office)
    except Class.DoesNotExist:
        #if the Class objects doesn't exits, it'll just create it
        """
        is_valid should be added.
        """
        c = Class.objects.create(division = division, grade = grade, office = office)
        c.save()
    
    try:
        newUser = GnumaUser.objects.get(user = user, classM = c)
    except GnumaUser.DoesNotExist:
        """
        is_valid should be added.
        """
        newUser = GnumaUser.objects.create(user = user, classM = c, adsCreated = 0, level = "Free")
        newUser.save()

    return JsonResponse({'detail' : 'GnumaUser successfully registered!'}, status = status.HTTP_201_CREATED)



@api_view(['POST',])
@authentication_classes([TokenAuthentication,])
@permission_classes([IsAuthenticated,])
@parser_classes([FileUploadParser,])
def upload_image(request, filename, format = None):
    '''
    Allowed images' types
    '''
    allowed_ext = ("image/png", "image/jpeg")
    #
    # token check
    #
    if not DoubleCheck(token = request.auth).is_valid():
        return JsonResponse({'detail' : 'your token has expired!'}, status = status.HTTP_403_FORBIDDEN)

    content_type = request.META['CONTENT_TYPE']
    content = request.data['file']
    if content_type == None or content_type not in allowed_ext:
        return JsonResponse({'detail' : 'extension not allowed!'}, status = status.HTTP_400_BAD_REQUEST)
    '''
    IS FILE SIZE ACCEPTABLE ?
    '''
    #content_length = int(request.META['CONTENT_LENGTH'])

    #if content_length != content.size:
    #    return JsonResponse({'detail' : 'image size does not coincide!'})

    global ImageQueue

    # debug information
    print(repr(ImageQueue))

    try:
        # must be tested 
        if not ImageQueue.get(request.user.username, False):
            ImageQueue[request.user.username] = []
            if len(ImageQueue[request.user.username]) > 4:
                # 5 images allowed
                return JsonResponse({'detail' : 'maximum number of images reached!'}, status = status.HTTP_409_CONFLICT)

        handler = ImageHandler(filename = filename, content = content, user = request.user, content_type = content_type)
        pk = handler.open()
        ImageQueue[request.user.username].append(pk)
    except Exception as e:
        print('An exception has been thrown: %s' % str(e))
        ImageQueue.pop(request.user.username, None)
        return JsonResponse({'detail' : 'something went wrong!'}, status = status.HTTP_400_BAD_REQUEST)
    
    return HttpResponse(status = status.HTTP_201_CREATED)
    
    
    
    

'''
-------------------------------------------------------------------------------------------------------------------+
                                                                                                                   |
Book Manager                                                                                                       |
                                                                                                                   |
-------------------------------------------------------------------------------------------------------------------+
'''

class BookManager(viewsets.GenericViewSet):

    authentication_classes = [TokenAuthentication]
    safe_actions = ('list', 'retrieve', 'search')
    lookup_field = 'isbn'
    queryset = Book.objects.all()

    def get_permissions(self):
        if self.action in self.safe_actions:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated] 
        return [permission() for permission in permission_classes]


    '''
    The following method tries to create a Book instance.
    If the Book that is going to be created already exists, it just does nothing.
    '''
    def create(self, request):
        '''
        The user must be authenticated to get access to this view, so request.user necessarily exists.
        '''
        if 'isbn' not in request.data or 'title' not in request.data or 'author' not in request.data:
            return JsonResponse({"detail":"one or more arguments are missing!"}, status = status.HTTP_400_BAD_REQUEST)
        user = GnumaUser.objects.get(user = request.user)
        try: 
            b = Book.objects.get(isbn = request.data['isbn'], classes = user.classM)
            return HttpResponse(status = status.HTTP_201_CREATED)
        except Book.DoesNotExist:
            try:     
                b = Book.objects.get(isbn = request.data['isbn'])
                b.classes.add(user.classM)
                return HttpResponse(status = status.HTTP_201_CREATED)
            except Book.DoesNotExist:
                b = Book.objects.create(title = request.data['title'], author = request.data['author'], isbn = request.data['isbn'])
                b.save()
                b.classes.add(user.classM)
                return HttpResponse(status = status.HTTP_201_CREATED)
  
    '''
    The following method lists all the Books instances.
    '''
    def list(self, request):
        serializer = BookSerializer(self.get_queryset(), many = True)
        return JsonResponse(serializer.data, status = status.HTTP_200_OK, safe = False)

    def retrieve(self, request, *args, **kwargs):
        book = self.get_object()
        serializer = BookSerializer(book, many = False)
        return JsonResponse(serializer.data, status = status.HTTP_200_OK, safe = False)
    
    '''
    @action(detail = False, methods = ['post'])
    def search(self, request):
        if 'keyword' not in request.data:
            return JsonResponse({"detail":"One or more arguments are missing!"}, status = status.HTTP_400_BAD_REQUEST)
        e = Engine(model = Book, lookup_field = 'title', keyword = request.data['keyword'], geo = False)
        book = e.get_candidates()
        serializer = BookSerializer(book, many = False)
        return JsonResponse(serializer.data, status = status.HTTP_200_OK, safe = False)
    '''
    
'''
-------------------------------------------------------------------------------------------------------------------+
                                                                                                                   |
Ad Manager                                                                                                         |
                                                                                                                   |
-------------------------------------------------------------------------------------------------------------------+
'''

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
    Enqueue the items that don't have a confirmed book related.
    '''
    def enqueue(self, request):
        user = GnumaUser.objects.get(user = request.user)

        instance = {'description': request.data['description'], 'price': request.data['price'], 'seller': user, 'enabled': False}
        if not self.get_serializer_class()(data = instance).is_valid():
            return HttpResponse(status = status.HTTP_400_BAD_REQUEST)
        enqueued = Ad.objects.create(**instance)
        instance = {'ad': enqueued, 'book_title': request.data['book_title'], 'isbn': request.data['isbn']}
        try:
            QueueAdsSerializer(data = instance).is_valid(raise_exception = True)
        except (ValidationError, TypeError) as e:
            print(str(e))
            return JsonResponse({'detail':'data is not valid!'}, status = status.HTTP_400_BAD_REQUEST)
        e = Queue_ads.objects.create(**instance)  
        e.save()
        enqueued.save()
        user.adsCreated = user.adsCreated+1
        user.save()

        
        image_pk_array = ImageQueue.pop(request.user.username, None)
        for img in image_pk_array:
            image = ImageAd.objects.get(pk = img)
            image.ad = enqueued
            image.save()
        
        return JsonResponse({'detail':'item enqueued!'}, status = status.HTTP_201_CREATED)



    '''
    The following method creates an item.

    The client should indicate whether the book has been selected from the hints.
    If it wasn't the client should add 'book_title' into the JSON object.
    Each request that has the 'book_title' creates an enqueued item, that eventually will be enabled by the staff.   
    '''
    def create(self, request):
        user = GnumaUser.objects.get(user = request.user)
        
        # Must be tested
        if not DoubleCheck(token = request.auth).is_valid():
            return JsonResponse({'detail' : 'your token has expired'}, status = status.HTTP_401_UNAUTHORIZED)

        # Check whether the user has reached his items' limit
        if user.level == "Free" and user.adsCreated == 10:
            return JsonResponse({'detail':'The user cannot insert any other item!'}, status = status.HTTP_403_FORBIDDEN)
        elif user.level == "Pro" and user.adsCreated == 20:
            return JsonResponse({'detail':'The user cannot insert any other item!'}, status = status.HTTP_403_FORBIDDEN)
        
        # Check the arguments' validity
        if 'description' not in request.data or 'price' not in request.data or 'isbn' not in request.data:
            return JsonResponse({"detail":"one or more arguments are missing!"}, status = status.HTTP_400_BAD_REQUEST)


        # If the book isn't in the database just enqueue the item
        if 'book_title' in request.data:
            return self.enqueue(request)
        

        # This get should never raise and exception, unless the endpoint hasn't been called by the React client.
        # WHITE_LIST CHECK
        try: 
            book = Book.objects.get(isbn = request.data['isbn'])
        except Book.DoesNotExist:
            return JsonResponse({'detail':'the book does not exist'}, status = status.HTTP_400_BAD_REQUEST)

        instance = {'description': request.data['description'], 'price': request.data['price'], 'book': book, 'seller': user}

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
        
        #
        # Relate the new item to its images, if it has any.
        # 
        image_pk_array = ImageQueue.pop(request.user.username, None)
        for img in image_pk_array:
            image = ImageAd.objects.get(pk = img)
            image.ad = newAd
            image.save()

        user.adsCreated = user.adsCreated+1
        user.save()
        
        return HttpResponse(status = status.HTTP_201_CREATED)


    def retrieve(self, request, *args, **kwargs):
        ad = self.get_object()
        serializer = self.get_serializer_class()(ad, many = False, context = {'request': request})
        return JsonResponse(serializer.data, status = status.HTTP_200_OK, safe = False)


    @action(detail = False, methods = ['post'])
    def search(self, request):
        #
        # The first step attempts to determine whether the user has chosen one of the hints or not.
        # If the POST request contains an 'isbn' key it means the user has effectively chosen one hints,
        # and then this view just returns the items related to the book with that isbn.
        # If the request does not contain the 'isbn' key, then this just tries to figure out what the user
        # may be looking for.
        #
        # This view returns items grouped by office.
        #

        if 'isbn' not in request.data and 'keyword' not in request.data:
            return JsonResponse({'detail':'one or more argument are missing!'})
        
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
            results = self.get_serializer_class()(ads, many = True)
            response['resultType'] = 'single'      
            response['results'] = results.data

            return JsonResponse(response, status = status.HTTP_200_OK, safe = False)
        else:
            return JsonResponse({'detail':'function are not implemented!'}, status = status.HTTP_400_BAD_REQUEST)
    


        

