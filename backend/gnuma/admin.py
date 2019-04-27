# django imports
from django.contrib import admin

# local imports
from .models import  Subject, GnumaUser, Office, Class, Ad, Book, Queue_ads, ImageAd, Comment
from .users_profiling.models import ItemAccess
from .chat.models import Chat, Message, Notification

admin.site.register(Ad)
admin.site.register(Class)
admin.site.register(Office)
admin.site.register(GnumaUser)
admin.site.register(Book)
admin.site.register(Queue_ads)
admin.site.register(ImageAd)
admin.site.register(Comment)
admin.site.register(ItemAccess)
admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(Subject)