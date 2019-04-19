from django.conf.urls import url

from .chat.chat import Chat

websocket_urlpatterns = [
    url(r'ws/chat/', Chat),
]