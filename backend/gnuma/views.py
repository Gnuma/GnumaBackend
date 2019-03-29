# OS imports
import os, sys

# Django imports
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.conf import settings

# Rest imports
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, action, parser_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import  IsAuthenticated , AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser

# Local imports
from .models import GnumaUser, Book, Office, Class, Ad, Queue_ads, ImageAd
from .serializers import BookSerializer, AdSerializer, QueueAdsSerializer
from .imageh import ImageHandler
from .doubleCheckLayer import DoubleCheck

# debug imports
import traceback


ImageQueue = {}


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
def upload_image(request, filename, format = None):
    '''
    Allowed images' types
    '''
    allowed_ext = ("image/png", "image/jpeg")
    if not DoubleCheck(token = request.auth).is_valid():
        return JsonResponse({'detail' : 'your token has expired!'}, status = status.HTTP_401_UNAUTHORIZED)

    content_type = request.META['CONTENT_TYPE']
    content = request.data['file']

    if content_type == None or content_type not in allowed_ext:
        return JsonResponse({'detail' : 'extension not allowed!'}, status = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    '''
    IS FILE SIZE ACCEPTABLE ?
    '''
    #content_length = int(request.META['CONTENT_LENGTH'])

    #if content_length != content.size:
    #    return JsonResponse({'detail' : 'image size does not coincide!'})

    try:
        handler = ImageHandler(content = content, content_type = content_type)
        pk = handler.open()
        print("PK loaded: " +str(pk))
    except Exception:
        traceback.print_exc()
        return JsonResponse({'detail' : 'something went wrong!'}, status = status.HTTP_400_BAD_REQUEST)

    return JsonResponse({'pk' : pk}, status = status.HTTP_201_CREATED)



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
        if 'isbn' not in request.data or 'title' not in request.data or 'author' not in request.data:
            return JsonResponse({"detail":"one or more arguments are missing!"}, status = status.HTTP_400_BAD_REQUEST)
        user = GnumaUser.objects.get(user = request.user)
        try: 
            b = Book.objects.get(isbn = request.data['isbn'], classes = user.classM)
            return JsonResponse({'detail' : 'book created!'}, status = status.HTTP_201_CREATED)
        except Book.DoesNotExist:
            try:     
                b = Book.objects.get(isbn = request.data['isbn'])
                b.classes.add(user.classM)
                return JsonResponse({'detail' : 'book created!'}, status = status.HTTP_201_CREATED)
            except Book.DoesNotExist:
                b = Book.objects.create(title = request.data['title'], author = request.data['author'], isbn = request.data['isbn'])
                b.save()
                b.classes.add(user.classM)
                return JsonResponse({'detail' : 'book created!'}, status = status.HTTP_201_CREATED)
  
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
        print("TYPE " + str(type(self)))
        if self.action in self.safe_actions:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated] 
        return [permission() for permission in permission_classes]
        

    
    def get_parsers(self):
        if self.action == 'create':
            parser_classes = MultiPartParser
        
        return [parser() for parser in parser_classes]


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
        enqueued.save()
        user.adsCreated = user.adsCreated+1
        user.save()

        if 'pks' in request.data:
            print(repr(request.data['pks']))
            for p_k in request.data['pks']:
                image = ImageAd.objects.get(pk = p_k)
                image.ad = newAd
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
       
        images = {}
        if request.data['0']:
            '''
            The request has at least one image attached.
            '''
            print("Immagini trovate nella richiesta")
            images['0'] = request.data['0']
            print(request.data['0'])
            images['0'] = request.data['0']
            i = 1
            while str(i) in request.data:
                images[str(i)] = request.data[str(i)]
                i += 1
            content_type = content_type = request.META['CONTENT_TYPE']
            image = ImageHandler(content = images, content_type = content_type)
            result = image.open()

        content_type = content_type = request.META['CONTENT_TYPE']
        result = ImageHandler(content = images, content_type = content_type)
        


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
        if image_pk_array != None:
            for img in image_pk_array:
                image = ImageAd.objects.get(pk = img)
                image.ad = newAd
                image.save()

        if 'pks' in request.data:
            print(repr(request.data['pks']))
            for p_k in request.data['pks']:
                image = ImageAd.objects.get(pk = p_k)
                image.ad = newAd
                image.save()

        user.adsCreated = user.adsCreated+1
        user.save()
        
        return JsonResponse({'detail' : 'item created!'}, status = status.HTTP_201_CREATED)


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
