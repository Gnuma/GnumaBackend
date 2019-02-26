# Django imports
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


# Rest imports
from rest_framework import status
from rest_framework.test import APITestCase, APITransactionTestCase
from rest_framework.authtoken.models import Token

# Local imports
from gnuma.views import upload_image
from .serializers import AdSerializer
from gnuma.models import Office, Class, GnumaUser, Book, Ad, Queue_ads, ImageAd


'''

The following classes have been succesfully tested.

TestCode: #3

'''
class InitUser(APITestCase):
    
    def setUp(self):
        user = User.objects.create_user(username = 'Gnuma', email = 'test@test.it', password = 'test')
        Token.objects.create(user = user, key = '12345')
        Office.objects.create(name = 'Neumann', cap = '00100', level = Office.SP)

    def test_init(self):
        url = reverse('init-user')
        data = {'key':'12345', 'classM': '5B', 'office': 'Neumann'}
        response = self.client.post(url, data)
        #
        # See results.
        #
        print("DEBUG INFORMATIONS:")
        for c in Class.objects.all():
            print("Class: %s%s related to %s" % (c.grade, c.division, c.office.name))

        for u in GnumaUser.objects.all():
            print("Name: %s School: %s%s %s" % (u.user.username, u.classM.grade, u.classM.division, u.classM.office.name))
        print('The server has issued a %s status code: %s' % (response.status_code,response.content))


class InitUserJSONError(APITestCase):

    def setUp(self):
        user = User.objects.create_user(username = 'Gnuma', email = 'test@test.it', password = 'test')
        Token.objects.create(user = user, key = '12345')
        Office.objects.create(name = 'Neumann', cap = '00100', level = Office.SP)
    
    def test_missing_argument(self):
        url = reverse('init-user')
        data = {'classM': '5B', 'office': 'Neumann'} # 'key' argument is missing
        response = self.client.post(url, data)
        print('The server has issued a %s status code: %s' % (response.status_code,response.content))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_format_error(self):
        url = reverse('init-user')
        data = {'key' : '12345', 'classM': '5BB', 'office': 'Neumann'} # 'class' argument isn't well-formed
        response = self.client.post(url, data)
        print('The server has issued a %s status code: %s' % (response.status_code,response.content))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class InitUserDataMissing(APITestCase):
    
    def test_token_missing(self):
        user = User.objects.create_user(username = 'Gnuma', email = 'test@test.it', password = 'test')
        # Token is not created : Token.objects.create(user = user, key = '12345')
        Office.objects.create(name = 'Neumann', cap = '00100', level = Office.SP)
        #
        # Request
        #
        url = reverse('init-user')
        data = {'key':'12345', 'classM': '5B', 'office': 'Neumann'}
        response = self.client.post(url, data)
        print('The server has issued a %s status code: %s' % (response.status_code,response.content))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_office_missing(self):
        user = User.objects.create_user(username = 'Gnuma', email = 'test@test.it', password = 'test')
        Token.objects.create(user = user, key = '12345')
        # Office is not created: Office.objects.create(name = 'Neumann', cap = '00100', level = Office.SP)
        #
        # Request
        #
        url = reverse('init-user')
        data = {'key':'12345', 'classM': '5B', 'office': 'Neumann'}
        response = self.client.post(url, data)
        print('The server has issued a %s status code: %s' % (response.status_code,response.content))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

'''

The following classes have been succesfully tested.

TestCode: #1

'''

class UploadImageTest(APITestCase):

    def setUp(self):
        user = User.objects.create_user(username = 'test', email = 'test@test.it', password = 'test')
        Token.objects.create(user = user, key = '12345')
        Office.objects.create(name = 'Neumann', cap = '00100', level = Office.SP)

    def test_upload(self):
        url = reverse('init-user')
        data = {'key':'12345', 'classM': '5B', 'office': 'Neumann'}
        response = self.client.post(url, data)
        print('The server has issued a %s status code: %s' % (response.status_code,response.content))
        i = 0
        for user in GnumaUser.objects.all():
            print("username %s" % user.user.username)
            i += 1
        print(str(i)+" items printed")
        url = reverse('upload-ad-image', kwargs={'filename':'image'})
        img = open(r"/home/free_will/Pictures/prgt.png", "rb").read()
        self.client.credentials(HTTP_AUTHORIZATION = 'Token 12345', CONTENT_TYPE = 'image/png')
        response = self.client.post(url, img, content_type = 'image/png')
        print("The API has issued an "+str(response.status_code)+" status code!")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UploadImageFails(APITestCase):

    def setUp(self):
        user = User.objects.create_user(username = 'test', email = 'test@test.it', password = 'test')
        Token.objects.create(user = user, key = '12345')
        Office.objects.create(name = 'Neumann', cap = '00100', level = Office.SP)

    def test_extension_fail(self):
        url = reverse('init-user')
        data = {'key':'12345', 'classM': '5B', 'office': 'Neumann'}
        response = self.client.post(url, data)
        print('The server has issued a %s status code: %s' % (response.status_code,response.content))
        url = reverse('upload-ad-image', kwargs={'filename':'image'})
        img = open(r"/home/free_will/Pictures/prgt.png", "rb").read()
        self.client.credentials(HTTP_AUTHORIZATION = 'Token 12345', CONTENT_TYPE = 'image/gif') # extension is not valid
        response = self.client.post(url, img, content_type = 'image/gif')
        print("The API has issued an %s status code: %s" % (str(response.status_code), response.content))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_double_enqueue(self):
        url = reverse('init-user')
        data = {'key':'12345', 'classM': '5B', 'office': 'Neumann'}
        response = self.client.post(url, data)
        print('The server has issued a %s status code: %s' % (response.status_code,response.content))
        #
        #   Upload two images without relating any item.
        #
        url = reverse('upload-ad-image', kwargs = {'filename' : 'image'})
        img = open(r"/home/free_will/Pictures/prgt.png", "rb").read()
        self.client.credentials(HTTP_AUTHORIZATION = 'Token 12345', CONTENT_TYPE = 'image/png') # extension is not valid
        response = self.client.post(url, img, content_type = 'image/png')
        print("The API has issued an %s status code: %s" % (str(response.status_code), response.content))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(url, img, content_type = 'image/png')
        print("The API has issued an %s status code: %s" % (str(response.status_code), response.content))
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)


#
# TestCode #2
#
# The following class contains all genuine requests to the AdManger endpoints.
#
class AdManagerTest(APITestCase):

    #
    # In order to make the following tests work, we have to do a big setUp here:
    #
    # 1) Create default User, Token, Office objects.
    #
    # 2) Make a request to init_user.
    #
    # 3) Create a Book object.
    #
    # 4) Upload image for the related item that test_create is going to create.
    #
    # 5) Create the Ad object that test_retrieve is going to retrieve.
    #
    
    def setUp(self):
        #
        # Default objects.
        #
        self.user = User.objects.create_user(username = 'test', email = 'test@test.it', password = 'test')
        Token.objects.create(user = self.user, key = '12345')
        Office.objects.create(name = 'Neumann', cap = '00100', level = Office.SP)
        for u in User.objects.all():
            print('username: %s' % u.username)
        #
        # request to init_user
        #
        url = reverse('init-user')
        data = {'key':'12345', 'classM': '5B', 'office': 'Neumann'}
        self.client.post(url, data)
        for g in GnumaUser.objects.all():
            print('gnumauser: %s' % g.user.username)
        #
        # Create Book object
        #
        Book.objects.create(title = 'Il canzoniere', author = 'Francesco Petrarca', isbn = '12345')
        #
        # Upload image
        #
        url = reverse('upload-ad-image', kwargs={'filename':'image'})
        img = open(r"/home/free_will/Pictures/prgt.png", "rb").read()
        self.client.credentials(HTTP_AUTHORIZATION = 'Token 12345', CONTENT_TYPE = 'image/png')
        self.client.post(url, img, content_type = 'image/png')
        #
        #  Create Ad object
        #
        seller = GnumaUser.objects.all()
        instance = {'title' : 'Retrieve test', 'price' : '45', 'seller' : seller[0], 'enabled' : True}
        try:
            AdSerializer(data = instance).is_valid(raise_exception = True)
        except Exception as e:
            print(str(e))
        self.assertEqual(AdSerializer(data = instance).is_valid(), True)
        ad = Ad.objects.create(**instance)
        self.id = ad.pk + 1
        print('id--->%d ' % ad.pk)
        



    #
    # The following method, create a complete item.
    # Tested successfully.
    #


    def test_create(self):

        url = reverse('ad-list')
        self.client.credentials(HTTP_AUTHORIZATION = 'Token 12345')
        data = {'title': 'Test', 'price' : '33', 'isbn': '12345'}
        response = self.client.post(url, data)
        print("The API has issued an %s status code: %s" % (str(response.status_code), response.content))

        for ad in Ad.objects.all():
            print(repr(ad.__dict__))
            self.id = ad.pk

        for img in ImageAd.objects.all():
            print(repr(img.__dict__))

        #
        # Check the number of ads created.
        #
        user = GnumaUser.objects.get(user = self.user)
        print('test_create : ' + repr(user.__dict__))

    
    def test_retrieve(self):

        url = reverse('ad-list')
        self.client.credentials(HTTP_AUTHORIZATION = 'Token 12345')
        data = {'title': 'Test', 'price' : '33', 'isbn': '12345'}
        response = self.client.post(url, data)
        print("The API has issued an %s status code: %s" % (str(response.status_code), response.content))

        for ad in Ad.objects.all():
            print(repr(ad.__dict__))
            self.id = ad.pk

        for img in ImageAd.objects.all():
            print(repr(img.__dict__))

        #
        # Check the number of ads created.
        #
        user = GnumaUser.objects.get(user = self.user)
        print('test_create : ' + repr(user.__dict__))

        url = reverse('ad-detail', kwargs = {'pk' : self.id})
        response = self.client.get(url)

        print(response.content)
    


class AdManagerNoImage(APITestCase):

    def setUp(self):
        #
        # Default objects.
        #
        self.user = User.objects.create_user(username = 'test', email = 'test@test.it', password = 'test')
        Token.objects.create(user = self.user, key = '12345')
        Office.objects.create(name = 'Neumann', cap = '00100', level = Office.SP)
        for u in User.objects.all():
            print('username: %s' % u.username)
        #
        # request to init_user
        #
        url = reverse('init-user')
        data = {'key':'12345', 'classM': '5B', 'office': 'Neumann'}
        self.client.post(url, data)
        for g in GnumaUser.objects.all():
            print('gnumauser: %s' % g.user.username)
        #
        # Create Book object
        #
        Book.objects.create(title = 'Il canzoniere', author = 'Francesco Petrarca', isbn = '12345')

    def test_create(self):
        url = reverse('ad-list')
        self.client.credentials(HTTP_AUTHORIZATION = 'Token 12345')
        data = {'title': 'Test', 'price' : '33', 'isbn': '12345'}
        response = self.client.post(url, data)
        print("The API has issued an %s status code: %s" % (str(response.status_code), response.content))

        for ad in Ad.objects.all():
            print(repr(ad.__dict__))

        #
        # Check the number of ads created.
        #
        user = GnumaUser.objects.get(user = self.user)
        print(repr(user.__dict__))

#
# TestCode #2
#
# The following class contains all erroneous requests to the AdManger endpoints.
#
class AdManagerFails(APITestCase):

    def setUp(self):
        #
        # Default objects.
        #
        self.user = User.objects.create_user(username = 'test', email = 'test@test.it', password = 'test')
        Token.objects.create(user = self.user, key = '12345')
        Office.objects.create(name = 'Neumann', cap = '00100', level = Office.SP)
        for u in User.objects.all():
            print('username: %s' % u.username)
        #
        # request to init_user
        #
        url = reverse('init-user')
        data = {'key':'12345', 'classM': '5B', 'office': 'Neumann'}
        self.client.post(url, data)
        for g in GnumaUser.objects.all():
            print('gnumauser: %s' % g.user.username)
        #
        # Create Book object
        #
        Book.objects.create(title = 'Il canzoniere', author = 'Francesco Petrarca', isbn = '12345')
        #
        # Upload image
        #
        url = reverse('upload-ad-image', kwargs={'filename':'image'})
        img = open(r"/home/free_will/Pictures/prgt.png", "rb").read()
        self.client.credentials(HTTP_AUTHORIZATION = 'Token 12345', CONTENT_TYPE = 'image/png')
        self.client.post(url, img, content_type = 'image/png')
        #
        #  Create Ad object
        #
        seller = GnumaUser.objects.all()
        instance = {'title' : 'Retrieve test', 'price' : '45', 'seller' : seller[0], 'enabled' : True}
        self.assertEqual(AdSerializer(data = instance).is_valid(), True)
        ad = Ad.objects.create(**instance)
        self.id = ad.pk
        print('id--->%d ' % ad.pk)


    def test_create_missing_argument(self):

        url = reverse('ad-list')
        self.client.credentials(HTTP_AUTHORIZATION = 'Token 12345')
        data = {'price' : '33', 'isbn': '12345'} # title key is missing
        response = self.client.post(url, data)
        print("The API has issued an %s status code: %s" % (str(response.status_code), response.content))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_bad_format(self):
        url = reverse('ad-list')
        self.client.credentials(HTTP_AUTHORIZATION = 'Token 12345')
        data = {'title' : 'test','price' : '3b', 'isbn': '12345'} # prce is not a valid integer
        response = self.client.post(url, data)
        print("The API has issued an %s status code: %s" % (str(response.status_code), response.content))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_book_not_found(self):

        url = reverse('ad-list')
        self.client.credentials(HTTP_AUTHORIZATION = 'Token 12345')
        data = {'title' : 'test','price' : '33', 'isbn': '1234'} # isbn is not valid
        response = self.client.post(url, data)
        print("The API has issued an %s status code: %s" % (str(response.status_code), response.content))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_ad_already_exist(self):
        #
        # First request
        #
        url = reverse('ad-list')
        self.client.credentials(HTTP_AUTHORIZATION = 'Token 12345')
        data = {'title': 'Test', 'price' : '33', 'isbn': '12345'}
        response = self.client.post(url, data)
        print("The API has issued an %s status code: %s" % (str(response.status_code), response.content))
        #
        # Second request
        #
        response = self.client.post(url, data)
        print("The API has issued an %s status code: %s" % (str(response.status_code), response.content))
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)


    def test_create_limit_reached(self):
        #
        # Edit 'ads_created'
        #
        gnumaUser = GnumaUser.objects.get( user = self.user )
        gnumaUser.adsCreated = 10
        gnumaUser.save()
        #
        # Request
        #
        url = reverse('ad-list')
        
        data = {'title': 'Test', 'price' : '33', 'isbn': '12345'}
        response = self.client.post(url, data)
        print("The API has issued an %s status code: %s" % (str(response.status_code), response.content))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#
# Test enqueue ads.
# TestCode #2
#
class EnqueueAdsTest(APITestCase):

    def setUp(self):
        #
        # Default objects.
        #
        self.user = User.objects.create_user(username = 'test', email = 'test@test.it', password = 'test')
        Token.objects.create(user = self.user, key = '12345')
        Office.objects.create(name = 'Neumann', cap = '00100', level = Office.SP)
        for u in User.objects.all():
            print('username: %s' % u.username)
        #
        # request to init_user
        #
        url = reverse('init-user')
        data = {'key':'12345', 'classM': '5B', 'office': 'Neumann'}
        self.client.post(url, data)
        for g in GnumaUser.objects.all():
            print('gnumauser: %s' % g.user.username)


    def test_enqueue(self):

        url = reverse('ad-list')
        self.client.credentials(HTTP_AUTHORIZATION = 'Token 12345')
        data = {'title': 'Test', 'price' : '33', 'isbn': '12345', 'book_title': 'Il canzoniere'}
        response = self.client.post(url, data)
        print("The API has issued an %s status code: %s" % (str(response.status_code), response.content))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for q in Queue_ads.objects.all():
            print(repr(q.__dict__))
            print('related ad:')
            print(repr(q.ad.__dict__))

        gnumaUser = GnumaUser.objects.get(user = self.user)
        print(repr(gnumaUser.__dict__))


#
# Test errors that enqueue method may raise.
#     
class EnqueueAdsFails(APITestCase):

    def setUp(self):
        #
        # Default objects.
        #
        self.user = User.objects.create_user(username = 'test', email = 'test@test.it', password = 'test')
        Token.objects.create(user = self.user, key = '12345')
        Office.objects.create(name = 'Neumann', cap = '00100', level = Office.SP)
        for u in User.objects.all():
            print('username: %s' % u.username)
        #
        # request to init_user
        #
        url = reverse('init-user')
        data = {'key':'12345', 'classM': '5B', 'office': 'Neumann'}
        self.client.post(url, data)
        for g in GnumaUser.objects.all():
            print('gnumauser: %s' % g.user.username)


    def test_enqueue_bad_format(self):
        url = reverse('ad-list')
        self.client.credentials(HTTP_AUTHORIZATION = 'Token 12345')
        data = {'title': 'Test', 'price' : '3b', 'isbn': '12345', 'book_title': 'Il canzoniere'} # price is not a valid integer
        response = self.client.post(url, data)
        print("The API has issued an %s status code: %s" % (str(response.status_code), response.content))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_enqueue_bad_format_2(self):

        url = reverse('ad-list')
        self.client.credentials(HTTP_AUTHORIZATION = 'Token 12345')
        data = {'title': 'Test', 'price' : '33', 'isbn': '12345678999999', 'book_title': 'Il canzoniere'} # isbn code isn't valid
        response = self.client.post(url, data)
        print("The API has issued an %s status code: %s" % (str(response.status_code), response.content))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

'''

The following class hasn't been tested yet.

TestCode: #4

'''

class DoubleCheckTest(APITestCase):

    def setUp(self):
        pass

