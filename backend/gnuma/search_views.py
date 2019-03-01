# django imports
from django.http import HttpResponse, JsonResponse

# rest imports
from rest_framework.decorators import api_view
from rest_framework import status

# haystack imports
from haystack.query import SearchQuerySet

# local imports
from .models import Book, Office
from .search_indexes import BookIndex

@api_view(['POST',])
def getHintsBooks(request):
    if 'keyword' not in request.data:
        return JsonResponse({'detail':'one or more arguments are missing!'}, status = status.HTTP_400_BAD_REQUEST)
    
    r = SearchQuerySet().autocomplete(title = request.data['keyword']).models(Book)
    if len(r) > 0:
        result = {}
        results = []
        for i in r:
            json_obj = {}
            json_obj['isbn'] = i.pk
            json_obj['title'] = i.title
            results.append(json_obj)
        result['results'] = results
        return JsonResponse(result, status = status.HTTP_200_OK)

    r = SearchQuerySet().autocomplete(isbn = request.data['keyword']).models(Book)
    if len(r) > 0:
        result = {}
        results = []
        for i in r:
            json_obj = {}
            json_obj['isbn'] = i.pk
            json_obj['title'] = i.title
            results.append(json_obj)
        result['results'] = results
        return JsonResponse(result, status = status.HTTP_200_OK)

    return JsonResponse({'results' : 'Nessun risultato!'}, status = status.HTTP_404_NOT_FOUND)

'''
@api_view(['POST'])
def getHintsOffices(request):
    if 'keyword' not in request.data:
        return JsonResponse({'detail':'one or more argument are missing!'}, status = status.HTTP_400_BAD_REQUEST)

    r = SearchQuerySet().autocomplete(content = request.data['keyword']).models(Office)

    if len(r) > 0:
        result = {}
        results = []
        for i in r:
            json_obj = {}
            json_obj['']
            results.append(json_obj)
        result['results'] = results
        return JsonResponse(result, status = status.HTTP_200_OK)
'''
