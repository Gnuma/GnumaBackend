# django imports
from django.contrib.auth.models import User

# rest imports
from rest_framework import serializers

# local imports
from .models import Chat, Message, Notification
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
    owner = ChatGnumaUserSerializer(many = False, read_only = True)
    chat = NotificationChatSerializer(many = False, read_only = True)

    class Meta:
        model = Message
        fields = '__all__'

