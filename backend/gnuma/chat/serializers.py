# django imports
from django.contrib.auth.models import User
from django.db.models import Max

# rest imports
from rest_framework import serializers
from rest_framework.fields import empty

# local imports
from .models import Chat, Message, Notification, Offert
from gnuma.models import GnumaUser, Ad, Comment, ImageAd
from gnuma.serializers import AdSerializer, AnswerSerializer, CommentSerializer, BookSerializer

#
# Notification serializers for ads
#

class NotificationAdSerializer(AdSerializer):
    class Meta:
        model = Ad
        fields = ('pk', 'seller', 'book', 'image_ad')

class ChatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', )

class ChatGnumaUserSerializer(serializers.ModelSerializer):
    user = ChatUserSerializer(many = False, read_only = False)
    _id = serializers.IntegerField(source = 'pk')

    class Meta:
        model = GnumaUser
        fields = ('_id' , 'user')

class ChatSerializer(serializers.ModelSerializer):
    buyer = ChatGnumaUserSerializer(read_only = True, many = False)
    item = NotificationAdSerializer(many = False, read_only = True)
    message_chat = serializers.SerializerMethodField()
    PAGE_SIZE = 20
    
    class Meta:
        model = Chat
        fields = '__all__'

    def get_message_chat(self, chat):
        current_page = self.context.get('page', 1) * self.PAGE_SIZE
        messages = Message.objects.filter(chat = chat).order_by('-created')[:current_page]

        return NotificationMessageSerializer(messages, many = True).data # does it work?

#
# Notification serializer for chats
#
class NotificationChatSerializer(ChatSerializer):
    class Meta:
        model = Chat
        fields = ('_id', 'item', 'buyer', 'createdAt')

#
# Notification serializer for answers and comments
#
class NotificationCommentSerializer(CommentSerializer):
    item = NotificationAdSerializer(many = False, read_only = True)

    class Meta:
        model = Comment
        fields = ('pk', 'item', 'createdAt')


class NotificationAnswerSerializer(AnswerSerializer):
    parent = NotificationCommentSerializer(many = False, read_only = True)

    class Meta:
        model = Comment
        fields = ('pk', 'parent', 'createdAt')

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class NotificationMessageSerializer(serializers.ModelSerializer):
    user = ChatGnumaUserSerializer(many = False, read_only = True)
    chat = NotificationChatSerializer(many = False, read_only = True)

    class Meta:
        model = Message
        fields = '__all__'

'''
The following serializer are going to be used in the 'retrieveChat' endpoint.
'''
class RetrieveMessageSerializer(serializers.ModelSerializer):
    user = ChatGnumaUserSerializer(many = False, read_only = True)
    class Meta:
        model = Message
        fields = ('_id', 'createdAt', 'is_read', 'text', 'user', 'system')

class RetrieveChatSerializer(serializers.ModelSerializer):
    buyer = ChatGnumaUserSerializer(many = False, read_only = True)
    messages = serializers.SerializerMethodField()
    hasNews = serializers.SerializerMethodField()
    PAGE_SIZE = 50
    
    class Meta:
        model = Chat
        fields = ('_id', 'buyer', 'hasNews', 'status', 'messages')
    
    def get_messages(self, chat):
        messages = Message.objects.filter(chat = chat).order_by('-createdAt')[:(self.PAGE_SIZE * self.context.get('page', 1))]
        return RetrieveMessageSerializer(messages, many = True).data

    def get_hasNews(self, chat):
        messages = Message.objects.filter(chat = chat, is_read = False)
        return messages.count()


class RetrieveAdSerializer(serializers.ModelSerializer):
    _id = serializers.IntegerField(source = 'pk')
    book = BookSerializer(many = False, read_only = True)
    chats = serializers.SerializerMethodField()
    seller = ChatGnumaUserSerializer(many = False, read_only = True)
    newsCount = serializers.SerializerMethodField()
    image_ad = serializers.SerializerMethodField()
    class Meta:
        model = Ad
        fields = ('_id', 'seller','book', 'newsCount', 'price', 'chats', 'condition', 'image_ad')

    #
    # get sales chats. Order items by the last message.
    #
    def get_chats(self, ad):
        if not self.context.get('user', False):
            chats = []
            seller_chats = Chat.objects.annotate(max = Max('messages__createdAt')).filter(item = ad).order_by('pk').order_by('-max')
            for chat in seller_chats:
                chats.append(RetrieveChatSerializer(chat, many = False).data)
            return chats
        else:
            user = self.context.get('user')
            chat = Chat.objects.get(buyer__user = user, item = ad)
            return RetrieveChatSerializer(chat, many = False).data

    def get_image_ad(self, ad):
        request = self.context.get('request')
        images = ImageAd.objects.filter(ad = ad)
        serialized_field = []

        for image in images:
            serialized_field.append(request.build_absolute_uri(image.image.url))
        
        return serialized_field
    
    def get_newsCount(self, ad):
        chats = Chat.objects.filter(item = ad)
        counter = 0
        for chat in chats:
            not_read_messages = Message.objects.filter(chat = chat, is_read = False)
            if not_read_messages:
                counter += 1
        return counter
#
# NewChat serializers
#

class RetrieveChatAdSerializer(RetrieveAdSerializer):

    #def __init__(self, instance=None, data=empty, **kwargs):
    #    delattr(self, "chats")
    #    super.__init__()
    
    class Meta:
        model = Ad
        fields = ('_id', 'seller','book', 'price',  'condition', 'image_ad')

class CreateChatSerializer(serializers.ModelSerializer):
    buyer = ChatGnumaUserSerializer(many = False, read_only = True)
    item = RetrieveChatAdSerializer(many = False, read_only = True)

    class Meta:
        model = Chat
        fields = ('_id', 'item','buyer', 'status')
    
class OffertSerializer(serializers.ModelSerializer):

    class Meta:
        model = Offert
        fields = '__all__'