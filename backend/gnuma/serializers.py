from rest_framework import serializers
from .models import GnumaUser, Book, Office, Class, Ad, Queue_ads, ImageAd
from django.contrib.auth.models import User



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username',)


class OfficeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Office
        fields = '__all__'


class ClassSerializer(serializers.ModelSerializer):
    office = OfficeSerializer(many = False, read_only = True)

    class Meta:
        model = Class
        fields = ['office']


class GnumaUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(many  = False, read_only = True)
    classM = ClassSerializer(many = False, read_only = True)
    class Meta:
        model = GnumaUser
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    classes = ClassSerializer(many = True, read_only = True) 

    class Meta:
        model = Book
        fields = ('isbn', 'title', 'author', 'classes')


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImageAd
        fields = ('created', 'image')


class AdSerializer(serializers.ModelSerializer):
    book = BookSerializer(many = False, read_only = True)
    seller = GnumaUserSerializer(many = False, read_only = True)
    image_ad = serializers.SlugRelatedField(many = True, read_only = True, slug_field = 'image')
    class Meta:
        model = Ad
        fields = ('description', 'book', 'seller', 'image_ad')


class QueueAdsSerializer(serializers.ModelSerializer):
    ad = AdSerializer(many = False, read_only = True)

    class Meta:
        model = Queue_ads
        fields = '__all__'

#
# The following serializers are used by the whoami API.
#
class WhoAmIGnumaUserSerializer(serializers.ModelSerializer):
    classM = ClassSerializer(many = False, read_only = True)

    class Meta:
        model = GnumaUser
        fields = ['classM']


class WhoAmISerializer(serializers.ModelSerializer):
    gnuma_user = WhoAmIGnumaUserSerializer(many = False, read_only = True)

    class Meta:
        model = User
        fields = ('username', 'email', 'gnuma_user')