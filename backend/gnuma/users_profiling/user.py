# django imports
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view, authentication_classes, action, parser_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import  IsAuthenticated

# rest imports
from rest_framework import status
from rest_framework.authtoken.models import Token

# local imports
from gnuma.models import GnumaUser
from gnuma.serializers import WhoAmISerializer
from gnuma.doubleCheck.doubleCheckLayer import DoubleCheck
from gnuma.users_profiling.itemAccess import BaseProfiling

#
# This endpoint is called by the client to retrieve information about the token it has received by the login endpoint.
#
@api_view(['GET',])
@authentication_classes([TokenAuthentication,])
@permission_classes([IsAuthenticated, ])
def whoami(request):
    if not DoubleCheck(token = request.auth).is_valid():
        return JsonResponse({'detail':'your token has expired!'}, status = status.HTTP_401_UNAUTHORIZED)

    s = WhoAmISerializer(request.user, many = False)
    return JsonResponse(s.data, status = status.HTTP_200_OK, safe = False)
    


#
# This endpoint is called by the client to retrieve information about its mailbox.
# It's going to return a list of comments and messages that the user hasn't read yet.
#
@api_view(['GET',])
@authentication_classes([TokenAuthentication,])
@permission_classes([IsAuthenticated, ])
def mailbox(request):
    if not DoubleCheck(token = request.auth).is_valid():
        return JsonResponse({'detail':'your token has expired!'}, status = status.HTTP_401_UNAUTHORIZED)

    instances = BaseProfiling.anynew({'user' : request.user})
    if instances:
        #
        # instances is an array provided with two elements:
        #
        # [0] contains the feeds about user's item's comments.
        # [1] contains the feeds about other users' items' comments.
        #
        response = {}
        response['mine'] = {}
        length = 0
        my_comments = []
        for f in instances[0]:
            length += 1
            my_comments.append({'item' : f, 'comment' : instances[0][f].pk, 'book_title' : instances[0][f].item.book.title, 'book_author' : instances[0][f].item.book.author})
        response['mine']['length'] = length
        response['mine']['results'] = my_comments

        response['others'] = {}
        length = 0
        others_comments = []
        for f in instances[1]:
            length += 1
            my_comments.append({'item' : f, 'comment' : instances[1][f].pk, 'book_title' : instances[1][f].item.book.title, 'book_author' : instances[1][f].item.book.author})
        response['others']['length'] = length
        response['others']['results'] = others_comments

        return JsonResponse(response, status = status.HTTP_200_OK)
    else:
        return HttpResponse('', status = status.HTTP_204_NO_CONTENT)
