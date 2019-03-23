# Python imports
import random

# Django imports
from django.conf import settings

# Local imports
from .models import ImageAd
from .serializers import ImageAdSerializer

# Pillow
from PIL import Image


class ImageHandler:

    def __init__(self, **kwargs):
        self.content_type = kwargs['content_type']
        self.content = kwargs['content']        # File obj


    def open(self, *args, **kwargs):
        with self.content.open() as f:
            instance = {'image' : f}

            serializer = ImageAdSerializer(data = instance)
            
            try:
                serializer.is_valid(raise_exception = True)
            except Exception:
                raise
            
            #
            # If the image is valid, just checks whether the type of the image is what we were said in the header.
            #
            # Note that PIL saves for the image's type during the DRF's validating process.
            #

            if self.content_type != serializer._validated_data['image'].content_type:
                #
                # The image type does not match with the one reported in the header
                #
                raise Exception
            instance = serializer.save()
            
            return instance.pk
    
    def resize(self, *args, **kwargs):
        pass
