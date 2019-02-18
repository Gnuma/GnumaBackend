from .models import GnumaUser, Book, Office, Class, Ad, Queue_ads
from django.conf import settings

'''
Must be tested

It probably isn't gonna work; and even if it does, I'm pretty sure that's not the best way to handle such a thing.

I'm using the database too many. Now I've just added this Queue thing, and even if it is bad as shit, it should actually work, so let's just hope that it will.
'''
class ImageHandler:

    content_types_dict = {
        'image/jpeg' : '.jpg',
        'image/png' : '.png'
    }

    def __init__(self, **kwargs):
        self.filename = kwargs['filename']
        self.content_type = self.content_types_dict.get(kwargs['content_type'], None)
        self.content = kwargs['content']
        self.user = kwargs['user']
        self.file_obj = None

        '''
        if '.' in self.filename:
            raise something
        '''

    def open(self, *args, **kwargs):
        n = str(Ad.objects.filter(seller = GnumaUser.objects.get(user=self.user)).count())
        f = open(r''.join([settings.IMAGES_DIR, self.user.username, '/',(''.join([self.filename, n, self.content_type]))]) , "wb")
        for byte in self.content.chunks():
            f.write(byte)
        f.close()
        return None
    
    def resize(self, *args, **kwargs):
        pass
