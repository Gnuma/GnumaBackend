# OS imports
import os, sys

# Django imports
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse

# Rest imports
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, action, parser_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import  IsAdmin
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FileUploadParser

# Local imports
from .models import GnumaUser, Book, Office, Class, Ad, Queue_ads
from .serializers import BookSerializer, AdSerializer
from .imageh import ImageHandler


class AdminAds(viewsets.ModelViewSet):

    serializer_class = AdSerializer
    queryset = Queue_ads.objects.all()
    permission_classes = [IsAdmin, ]

    @action(detail = True, methods = ['post'])
    def enableAd(self, *args, **kwargs):
        queued_ad = self.get_object()
        enabled_ad = queued_ad.ad
        isbn = queued_ad.isbn
        book_title = queued_ad.book_title
        

        # Create the submitted book

        instance = {'isbn': isbn, 'title': book_title}

        if not BookSerializer(data = instance).is_valid():
            return JsonResponse({'detail':'something went wrong!'}, status = status.HTTP_400_BAD_REQUEST)
        
        book = Book.objects.create(**instance)
        book.save()
        enabled_ad.book = book
        enabled_ad.enabled = True
        enabled_ad.save()

        return HttpResponse(status = status.HTTP_200_OK)





        