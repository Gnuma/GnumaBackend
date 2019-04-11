# django imports
from django.contrib import admin

# local imports
from .models import  GnumaUser, Office, Class, Ad, Book, Queue_ads, ImageAd, Comment
from .users_profiling.models import ItemAccess

admin.site.register(Ad)
admin.site.register(Class)
admin.site.register(Office)
admin.site.register(GnumaUser)
admin.site.register(Book)
admin.site.register(Queue_ads)
admin.site.register(ImageAd)
admin.site.register(Comment)
admin.site.register(ItemAccess)