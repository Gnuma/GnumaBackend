# django imports
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, action, parser_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import  IsAuthenticated

# rest imports
from rest_framework import status
from rest_framework.authtoken.models import Token

# local imports
from .models import GnumaUser
from .serializers import WhoAmISerializer
from .doubleCheckLayer import DoubleCheck


@api_view(['GET',])
@authentication_classes([TokenAuthentication,])
@permission_classes([IsAuthenticated, ])
def whoami(request):
    if not DoubleCheck(token = request.auth).is_valid():
        return JsonResponse({'detail':'your token has expired!'}, status = status.HTTP_401_UNAUTHORIZED)

    s = WhoAmISerializer(request.user, many = False)
    return JsonResponse(s.data, status = status.HTTP_200_OK, safe = False)
    