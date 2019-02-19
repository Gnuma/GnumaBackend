from rest_framework import serializers
from .models import GnumaUser, Book, Office, Class, Ad, Queue_ads
from django.contrib.auth.models import User



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

class GnumaUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(many  = False, read_only = True)

    class Meta:
        model = GnumaUser
        fields = '__all__'

class OfficeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Office
        fields = '__all__'


class ClassSerializer(serializers.ModelSerializer):
    office = OfficeSerializer(many = False, read_only = True)

    class Meta:
        model = Class
        fields = '__all__'



class BookSerializer(serializers.ModelSerializer):
    classes = ClassSerializer(many = True, read_only = True) 

    class Meta:
        model = Book
        fields = ('isbn', 'title', 'author', 'classes')


class AdSerializer(serializers.ModelSerializer):
    book = BookSerializer(many = False, read_only = True)
    seller = GnumaUserSerializer(many = False, read_only = True)

    class Meta:
        model = Ad
        fields = '__all__'


class QueueAdsSerializer(serializers.ModelSerializer):
    ad = AdSerializer(many = False, read_only = True)

    class Meta:
        model = Queue_ads
        fields = '__all__'