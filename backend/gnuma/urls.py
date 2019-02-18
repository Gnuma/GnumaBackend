from django.urls import path, include
from rest_framework import routers
from .views import BookManager, AdManager, init_user, upload_image

router = routers.SimpleRouter()
router.register(r'books', BookManager, basename = "book")
router.register(r'ads', AdManager)

urlpatterns = [
    path('init/', init_user, name = 'init-user'),
    path(r'ads/upload/<filename>/', upload_image, name = 'upload-ad-image')
]

urlpatterns += router.urls