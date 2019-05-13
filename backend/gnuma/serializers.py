# django import
from django.contrib.auth.models import User

# rest imports
from rest_framework import serializers

# local imports
from .models import GnumaUser, Subject, Book, Office, Class, Ad, Queue_ads, ImageAd, Comment
from .core.customFields import Base64ImageField



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
    _id = serializers.IntegerField(source = 'pk')

    class Meta:
        model = GnumaUser
        fields = ('_id', 'user', 'classM')

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(many = False, read_only = True)

    class Meta:
        model = Book
        fields = ('isbn', 'title', 'author', 'subject')


#
# The following serializer are used by the comments' subsystem.
#
class AnswerSerializer(serializers.ModelSerializer):
    user = GnumaUserSerializer(many = False, read_only = True)

    class Meta:
        model = Comment
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    user = GnumaUserSerializer(many = False, read_only = True)
    parent_child = AnswerSerializer(many = True, read_only = True) 
    parent = AnswerSerializer(many = False, read_only = True)

    class Meta:
        model = Comment
        fields = ('pk', 'user', 'text', 'parent_child', 'createdAt', 'parent')



class AdSerializer(serializers.ModelSerializer):
    book = BookSerializer(many = False, read_only = True)
    seller = GnumaUserSerializer(many = False, read_only = True)
    image_ad = serializers.SerializerMethodField()
    comment_ad = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = ('pk', 'description', 'price', 'condition', 'book', 'seller', 'image_ad', 'comment_ad')

    def get_image_ad(self, ad):
        request = self.context.get('request')
        images = ImageAd.objects.filter(ad = ad)
        serialized_field = []

        for image in images:
            serialized_field.append(request.build_absolute_uri(image.image.url))
        
        return serialized_field
    
    def get_comment_ad(self, ad):
        comments = Comment.objects.filter(item = ad).order_by('-createdAt')
        serialized_field = []

        for c in comments:
            serialized_field.append(CommentSerializer(c, many = False).data)
        
        return serialized_data


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
        fields = ('pk' ,'username', 'email', 'gnuma_user')


#
# The following serializer is used by the AdManager.create endpoint in order to upload an image.
#
# Base64ImageField is parser which enable the client upload base64-encoded images. 
#
class ImageAdSerializer(serializers.ModelSerializer):   
    image = Base64ImageField(max_length=None, use_url=True,)
    
    class Meta:
        model = ImageAd
        fields = '__all__'

