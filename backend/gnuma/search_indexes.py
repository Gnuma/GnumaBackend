# OS imports
import datetime

# Haystack
from haystack import indexes

from .models import Office, Book

#
# search indexes
#
class BookIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document = True, use_template = True)
    author = indexes.CharField(model_attr = 'author')
    #
    # renderer
    # 

    title = indexes.EdgeNgramField(model_attr = 'title')
    isbn = indexes.EdgeNgramField(model_attr = 'isbn')
    
    def get_model(self):
        return Book

    def index_queryset(self, using = None):
        return self.get_model().objects.all()


class OfficeIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document = True, model_attr = 'name')


    def get_model(self):
        return Office

    def index_queryset(self, using = None):
        return self.get_model().objects.all()