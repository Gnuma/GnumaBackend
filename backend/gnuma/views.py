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
from .models import GnumaUser, Book, Office, Class, Ad, Queue_ads
from .serializers import BookSerializer, AdSerializer, QueueAdsSerializer
from .imageh import ImageHandler
from .doubleCheckLayer import DoubleCheck


ImageQueue = {}


@api_view(['POST',])
@authentication_classes([TokenAuthentication,])
def init_user(request):
    if 'key' not in request.data or 'classM' not in request.data or 'office' not in request.data:
        return JsonResponse({"detail":"one or more arguments are missing!"}, status = status.HTTP_400_BAD_REQUEST)
    try:
        token = Token.objects.get(key = request.data['key'])
    except Token.DoesNotExist:
        return HttpResponse('key does not exist', status = status.HTTP_400_BAD_REQUEST)
    user = User.objects.get(username = token.user)
    classM = request.data['classM'] 
    try:
        office = Office.objects.get(name=request.data['office'])
    except Office.DoesNotExist:
        return HttpResponse("office does not exist", status = status.HTTP_400_BAD_REQUEST)
    if len(classM) != 2:
        return HttpResponse('class: format-error', status = status.HTTP_400_BAD_REQUEST)
    grade = classM[0]
    division = classM[1]
    try:
        c = Class.objects.get(division = division, grade = grade, office = office)
    except Class.DoesNotExist:
        #if the Class objects doesn't exits, it'll just create it
        c = Class.objects.create(division = division, grade = grade, office = office)
        c.save()
    try:
        newUser = GnumaUser.objects.get(user = user, classM = c)
    except GnumaUser.DoesNotExist:
        newUser = GnumaUser.objects.create(user = user, classM = c, adsCreated = 0, level = "Free")
        
        #Create the directory for images.
        try: 
            os.mkdir(r''.join([settings.IMAGES_DIR, user.username, '/']))          # ---------------------------------------> MUST BE TESTED
        except Exception as e:
            newUser.save() # To be deleted
            return HttpResponse(str(e), status = status.HTTP_403_FORBIDDEN)
        newUser.save()
    return HttpResponse(status = status.HTTP_201_CREATED)



@api_view(['POST',])
@authentication_classes([TokenAuthentication,])
@permission_classes([IsAuthenticated,])
@parser_classes([FileUploadParser,])
def upload_image(request, filename, format = None):
    '''
    Allowed images' types
    '''
    allowed_ext = ("image/png", "image/jpeg")

    # Must be tested
    if not DoubleCheck(token = request.auth).is_valid():
        return JsonResponse({'detail' : 'your token has expired'}, status = status.HTTP_403_FORBIDDEN)

    if request.content_type == None or request.content_type not in allowed_ext:
        return JsonResponse({"detail":"extension not allowed"}, status = status.HTTP_400_BAD_REQUEST)
    '''
    IS FILE SIZE ACCEPTABLE ?
    '''
    global ImageQueue

    if ImageQueue.get(request.user.username, False):
        return JsonResponse({'detail':'this user has already uploaded an image!'}, status = status.HTTP_409_CONFLICT)
    try:
        handler = ImageHandler(filename = filename, content = request.data['file'], user = request.user, content_type = request.content_type)
        filename = handler.open()
        ImageQueue[request.user.username] = request.build_absolute_uri(r''.join(('/',settings.IMAGES_URL, request.user.username,'/', filename)))
    except Exception:
        ImageQueue.pop(request.user.username)
        return JsonResponse({'detail' : 'something went wrong!'}, status = status.HTTP_400_BAD_REQUEST)
    
    return HttpResponse(status = status.HTTP_201_CREATED)
    


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
    
    @action(detail = False, methods = ['post'])
    def search(self, request):
        if 'keyword' not in request.data:
            return JsonResponse({"detail":"One or more arguments are missing!"}, status = status.HTTP_400_BAD_REQUEST)
        e = Engine(model = Book, lookup_field = 'title', keyword = request.data['keyword'], geo = False)
        book = e.get_candidates()
        serializer = BookSerializer(book, many = False)
        return JsonResponse(serializer.data, status = status.HTTP_200_OK, safe = False)



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


    def enqueue(self, request):
        user = GnumaUser.objects.get(user = request.user)
        image = ImageQueue.pop(request.user.username, None)
        instance = {'title': request.data['title'], 'price': request.data['price'], 'seller': user, 'enabled': False, 'image': image}
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
        return JsonResponse({'detail':'item enqueued!'}, status = status.HTTP_201_CREATED)


    def create(self, request):
        user = GnumaUser.objects.get(user = request.user)
        if not DoubleCheck(token = request.auth).is_valid():
            return JsonResponse({'detail' : 'your token has expired'}, status = status.HTTP_401_UNAUTHORIZED) # Returns the same as user's limit reached. Must be changed


        if user.level == "Free" and user.adsCreated == 10:
            return JsonResponse({'detail':'The user cannot insert any other item!'}, status = status.HTTP_403_FORBIDDEN)
        elif user.level == "Pro" and user.adsCreated == 20:
            return JsonResponse({'detail':'The user cannot insert any other item!'}, status = status.HTTP_403_FORBIDDEN)
        
        if 'title' not in request.data or 'price' not in request.data or 'isbn' not in request.data:
            return JsonResponse({"detail":"one or more arguments are missing!"}, status = status.HTTP_400_BAD_REQUEST)

        if 'book_title' in request.data:
            return self.enqueue(request)
        
        try: 
            book = Book.objects.get(isbn = request.data['isbn'])
        except Book.DoesNotExist:
            return JsonResponse({'detail':'the book does not exist'}, status = status.HTTP_400_BAD_REQUEST)

        image = ImageQueue.pop(request.user.username, None)
        instance = {'title': request.data['title'], 'image': image,'price': request.data['price'], 'book': book, 'seller': user}

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
        
        user.adsCreated = user.adsCreated+1
        user.save()
        
        return HttpResponse(status = status.HTTP_201_CREATED)


    def retrieve(self, request, *args, **kwargs):
        ad = self.get_object()
        serializer = self.get_serializer_class()(ad, many = False)
        return JsonResponse(serializer.data, status = status.HTTP_200_OK, safe = False)


    @action(detail = False, methods = ['post'])
    def search(self, request):
        if 'keyword' not in request.data:
            return JsonResponse({"detail":"One or more arguments are missing!"}, status = status.HTTP_400_BAD_REQUEST)
        e = Engine(model = Book, lookup_field = 'title', keyword = request.data['keyword'], geo = False)
        book = e.get_candidates()
        serializer = self.get_serializer_class()(Ad.objects.filter(book = book), many = True)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe = False)

    
    @action(detail = False, methods = ['post'])
    def geo_search(self, request):
        return JsonResponse({'detail':'this service is not available'}, status = status.HTTP_403_FORBIDDEN)