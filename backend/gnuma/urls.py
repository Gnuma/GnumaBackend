# Django imports
from django.urls import path, include

# Rest imports
from rest_framework import routers

# Local imports
from .views import BookManager, AdManager, init_user
from .users_profiling.user import whoami
from .search_engine.search_views import getHintsBooks, getHintsOffices
from .users_profiling.comments.commentsEndpoints import CommentsEndpoints

router = routers.SimpleRouter()
router.register(r'books', BookManager, basename = "book")
router.register(r'ads', AdManager)
router.register(r'comments', CommentsEndpoints)



urlpatterns = [
    path(r'init/', init_user, name = 'init-user'),
    path(r'search/hints/book/', getHintsBooks),
    path(r'search/hints/office/', getHintsOffices),
    path(r'whoami/', whoami)
]

urlpatterns += router.urls


