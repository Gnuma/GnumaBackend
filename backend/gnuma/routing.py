from django.conf.urls import url

from .chat.chat import BasicChatConsumer

websocket_urlpatterns = [
    url(r'ws/chat/', BasicChatConsumer),
]