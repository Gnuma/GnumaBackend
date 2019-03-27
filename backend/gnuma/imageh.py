# Python imports
import random
import io

# Django imports
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

# Local imports
from .models import ImageAd
from .serializers import ImageAdSerializer

# Pillow
from PIL import Image


class ImageHandler:

    def __init__(self, **kwargs):
        self.content_type = kwargs['content_type']
        self.content = kwargs["data"]
    def open(self, *args, **kwargs):
        instances = []
        for i in range(self.content.len()):
            content = {}
            content['content'] = self.content[str(i)]
            instance = {'image' : content}

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

            #if self.content_type != serializer._validated_data['image'].content_type:
                #
                # The image type does not match with the one reported in the header
                #
                #raise Exception
            instances.append(serializer.save())
            
            return instances
    
    def resize(self, *args, **kwargs):
        pass
