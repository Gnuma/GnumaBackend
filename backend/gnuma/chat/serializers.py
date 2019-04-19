# django imports
from django.contrib.auth.models import User

# rest imports
from rest_framework import serializers

# local imports
from .models import Chat, Message
from gnuma.models import GnumaUser, Ad, Comment
from gnuma.serializers import AdSerializer, AnswerSerializer, CommentSerializer

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

    class Meta:
        model = GnumaUser
        fields = ('pk' , 'user')

class MessageSerializer(serializers.ModelSerializer):
    owner = ChatUserSerializer(many = False, read_only = False)

    class Meta:
        model = Message
        fields = '__all__'

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

        return MessageSerializer(messages, many = True).data

#
# Notification serializer for chats
#
class NotificationChatSerializer(ChatSerializer):
    class Meta:
        model = Chat
        fields = ('pk', 'item', 'buyer', 'created')

#
# Notification serializer for answers and comments
#
class NotificationCommentSerializer(CommentSerializer):
    item = NotificationAdSerializer(many = False, read_only = True)

    class Meta:
        model = Comment
        fields = ('pk', 'item', 'user', 'created', 'content')


class NotificationAnswerSerializer(AnswerSerializer):
    parent = NotificationCommentSerializer(many = False, read_only = True)

    class Meta:
        model = Comment
        fields = ('pk', 'parent', 'user', 'content')

