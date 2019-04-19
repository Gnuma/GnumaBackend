# Django imports
from django.urls import path, include

# Rest imports
from rest_framework import routers

# Local imports
from .ads.AdManager import AdManager
from .users_profiling.user import whoami, init_user
from .search_engine.search_views import getHintsBooks, getHintsOffices
from .users_profiling.comments.commentsEndpoints import CommentsEndpoints
from .chat.rest import ChatsHandling

router = routers.SimpleRouter()
router.register(r'ads', AdManager)
router.register(r'comments', CommentsEndpoints)
router.register(r'chat', ChatsHandling)



urlpatterns = [
    path(r'init/', init_user, name = 'init-user'),
    path(r'search/hints/book/', getHintsBooks),
    path(r'search/hints/office/', getHintsOffices),
    path(r'whoami/', whoami)
]

urlpatterns += router.urls


