from django.contrib import admin
from .models import  GnumaUser, Office, Class, Ad, Book, Queue_ads

admin.site.register(Ad)
admin.site.register(Class)
admin.site.register(Office)
admin.site.register(GnumaUser)
admin.site.register(Book)
admin.site.register(Queue_ads)