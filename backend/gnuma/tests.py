# Django imports
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


# Rest imports
from rest_framework import status
from rest_framework.test import APITransactionTestCase, APITestCase
from rest_framework.authtoken.models import Token

# Local imports
from gnuma.views import upload_image
from gnuma.models import Office, Class, GnumaUser


'''

The following class has been succesfully tested.

TestCode: #3

'''
class InitUser(APITestCase):
    
    def setUp(self):
        user = User.objects.create_user(username = 'test', email = 'test@test.it', password = 'test')
        Token.objects.create(user = user, key = '12345')
        Office.objects.create(name = 'Neumann', cap = '00100', level = Office.SP)

    def test_init(self):
        url = reverse('init-user')
        data = {'key':'12345', 'classM': '5B', 'office': 'Neumann'}
        response = self.client.post(url, data)
        print('The server has issued a %s status code: %s' % (response.status_code,response.content))


'''

The following class has been succesfully tested.

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
        self.client.credentials(HTTP_AUTHORIZATION = 'Token 12345', CONTENT_TYPE = 'image/gif')
        response = self.client.post(url, img, content_type = 'image/png')
        print("The API has issued an "+str(response.status_code)+" status code!")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


'''

The following class hasn't been tested yet.

TestCode: #4

'''

class DoubleCheckTest(APITestCase):

    def setUp(self):
        pass

