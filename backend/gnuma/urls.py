# Django imports
from django.urls import path, include

# Rest imports
from rest_framework import routers

# Local imports
from .views import BookManager, AdManager, init_user, upload_image
from .user import whoami
from .search_views import getHintsBooks, getHintsOffices

router = routers.SimpleRouter()
router.register(r'books', BookManager, basename = "book")
router.register(r'ads', AdManager)



urlpatterns = [
    path(r'init/', init_user, name = 'init-user'),
    path(r'ads/upload/<filename>/', upload_image, name = 'upload-ad-image'),
    path(r'search/hints/book/', getHintsBooks),
    path(r'search/hints/office/', getHintsOffices),
    path(r'whoami/', whoami)
]

urlpatterns += router.urls


