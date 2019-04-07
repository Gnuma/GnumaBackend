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
from gnuma.models import GnumaUser, Office, Class
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

    i = {'user' : request.user}
    instances = BaseProfiling.anynew(**i)
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



@api_view(['POST',])
@authentication_classes([TokenAuthentication,])
def init_user(request):
    if 'key' not in request.data or 'classM' not in request.data or 'office' not in request.data:
        return JsonResponse({'detail':'one or more arguments are missing!'}, status = status.HTTP_400_BAD_REQUEST)

    try:
        token = Token.objects.get(key = request.data['key'])
    except Token.DoesNotExist:
        return JsonResponse({'detail' : 'key does not exist!'}, status = status.HTTP_400_BAD_REQUEST)

    user = User.objects.get(username = token.user)
    classM = request.data['classM'] 
    try:
        office = Office.objects.get(name = request.data['office'])
    except Office.DoesNotExist:
        return JsonResponse({'detail' : 'office does not exits!'}, status = status.HTTP_400_BAD_REQUEST)

    if len(classM) != 2:
        return JsonResponse({'detail' : 'invalid format!'}, status = status.HTTP_400_BAD_REQUEST)

    grade = classM[0]
    division = classM[1]
    try:
        c = Class.objects.get(division = division, grade = grade, office = office)
    except Class.DoesNotExist:
        #if the Class objects doesn't exits, it'll just create it
        """
        is_valid should be added.
        """
        c = Class.objects.create(division = division, grade = grade, office = office)
        c.save()
    
    try:
        newUser = GnumaUser.objects.get(user = user, classM = c)
    except GnumaUser.DoesNotExist:
        """
        is_valid should be added.
        """
        newUser = GnumaUser.objects.create(user = user, classM = c, adsCreated = 0, level = "Free")
        newUser.save()

    return JsonResponse({'detail' : 'GnumaUser successfully registered!'}, status = status.HTTP_201_CREATED)
