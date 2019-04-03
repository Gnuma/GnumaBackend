# django imports
from django.http import HttpResponse, JsonResponse

# rest imports
from rest_framework.decorators import api_view
from rest_framework import status

# haystack imports
from haystack.query import SearchQuerySet

# local imports
from gnuma.models import Book, Office
from .search_indexes import BookIndex


#
# keyword: the user can enter either the book's name or its isbn.
#
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

#
# keyword: the user can enter the office's name.
#
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
            json_obj['id'] = i.pk
            json_obj['name'] = i.text
            json_obj['cap'] = Office.objects.get(pk = i.pk).cap
            results.append(json_obj)
        result['results'] = results
        return JsonResponse(result, status = status.HTTP_200_OK)

    #
    # If there's no match the API just returns a blank list.
    #    
    json_obj = {}
    return JsonResponse({'results' : json_obj}, status = status.HTTP_404_NOT_FOUND)



    
