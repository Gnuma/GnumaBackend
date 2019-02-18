from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('gnuma/v1/auth/', include('rest_auth.urls')), #login management
    path('gnuma/v1/auth/registration/', include('rest_auth.registration.urls')), #signup management
    path('gnuma/v1/', include('gnuma.urls'))
] + static(settings.IMAGES_URL, document_root = settings.IMAGES_DIR)


