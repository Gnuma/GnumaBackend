# Python imports
import random

# Django imports
from django.conf import settings

# Local imports
from .models import ImageAd

# Pillow
from PIL import Image


class ImageHandler:

    content_types_dict_dot = {
        'image/jpeg' : '.jpg',
        'image/png' : '.png'
    }

    content_types_dict_PIL = {
        'image/jpeg': 'JPEG',
        'image/png': 'PNG'
    }

    def __init__(self, **kwargs):
        self.filename = kwargs['filename']
        self.content_type_dot = self.content_types_dict_dot.get(kwargs['content_type'], None)
        self.content_type = self.content_types_dict_PIL.get(kwargs['content_type'], None)
        self.content = kwargs['content']        # File obj
        self.user = kwargs['user']

        '''
        if '.' in self.filename:
            raise something
        '''

    def open(self, *args, **kwargs):
        n = str(random.randint(0,400))
        newFilename =''.join([self.filename, '_', n, self.content_type_dot])

        with self.content.open() as f:
            try:
                i = Image.open(f)
            except Exception:
                print("Cannot open the image")
                raise
            #
            # If the image type is not what we expected just return 400.
            #
            if i.format != self.content_type:
                print("Bad format")
                i.close()
                raise Exception         # Must be changed
            #
            # Let's create a new ImageAd
            #
            # Must be tested
            #
            newImage = ImageAd.objects.create()
            newImage.save()
            newImage.image.save(newFilename, f)
            return newImage.pk
    
    def resize(self, *args, **kwargs):
        pass
