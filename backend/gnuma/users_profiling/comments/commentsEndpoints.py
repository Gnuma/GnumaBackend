# Django imports
from django.http import JsonResponse


# Rest imports
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import  IsAuthenticated , AllowAny
from rest_framework.decorators import action

# local imports
from .comments import CommentHandler
from gnuma.models import Comment



#
# This class contains every comments' endpoint.
#
class CommentsEndpoints(viewsets.GenericViewSet):
    safe_actions = ['retrieve']
    queryset = Comment.objects.all()
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.action in self.safe_actions:
            permission_classes = [AllowAny, ]
        else:
            permission_classes = [IsAuthenticated, ]

        return [permission() for permission in permission_classes]

    
    def create(self, request):
        if 'item' not in request.data or 'content' not in request.data or 'type' not in request.data:
            return JsonResponse({'detail' : 'one or more arguments are missing!'}, status = status.HTTP_400_BAD_REQUEST)
        
        if request.data['type'] == 'comment':
            instance = {'item' : request.data['item'], 'content' : request.data['content'], 'user' : request.user, 'request' : request}
            try:
                comment = CommentHandler.create(**instance)
                return JsonResponse({'pk' : comment.pk, 'timestamp' : comment.createdAt}, status = status.HTTP_201_CREATED)
            except Exception as e:
                print(str(e))
                return JsonResponse({'detail' : 'something went wrong!'}, status = status.HTTP_400_BAD_REQUEST)
        elif request.data['type'] == 'answer':
            #
            # In this case 'item' represents the parent comment.
            #
            instance = {'comment' : request.data['item'], 'content' : request.data['content'], 'user' : request.user, 'request' : request}
            try:
                answer = CommentHandler.create_answer(**instance)
                return JsonResponse({'pk' : answer.pk, 'timestamp' : answer.createdAt}, status = status.HTTP_201_CREATED)
            except Exception as e:
                print(str(e))
                return JsonResponse({'detail' : 'something went wrong!'}, status = status.HTTP_400_BAD_REQUEST)


    @action(detail = False, methods = ['post'])
    def report(self, request):
        if 'content' not in request.data or 'comment' not in request.data:
            return JsonResponse({'detail' : 'one or more arguments are missing!'}, status = status.HTTP_400_BAD_REQUEST)

        try:
            if not CommentHandler.report({'content' : request.data['content'], 'comment' : request.data['comment'], 'user' : request.user}):
                return JsonResponse({'detail' : 'you have already reported this comment!'}, status = status.HTTP_403_FORBIDDEN)
            return JsonResponse({'detail' : 'comment reported!'})
        except Exception as e:
            print(str(e))
            return JsonResponse({'detail' : 'something went wrong!'}, status = status.HTTP_400_BAD_REQUEST)
