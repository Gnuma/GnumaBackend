#
#  This file contains the comments' subsystem.
#

from gnuma.models import Comment, Ad, Report, GnumaUser
from gnuma.serializers import CommentSerializer

class CommentHandler(object):
    
    #
    # Parameters:
    # 
    # item : item's pk.
    # content: the comment's content.
    # user: GnumaUser object.
    #
    @staticmethod
    def create(*args, **kwargs):
        try:
            item_pk = kwargs['item']
            user = GnumaUser.objects.get(user = kwargs['user'])
            content = kwargs['content']
            item = Ad.objects.get(pk = item_pk)
        except KeyError:
            raise
        except Ad.DoesNotExist:
            raise
        
        instance = {'content' : content, 'item' : item_pk, 'user' : user}
        comment = CommentSerializer(data = instance)

        try:
            comment.is_valid(raise_exception = True)
        except Exception:
            raise

        instance['item'] = item
        newComment = Comment(**instance)
        newComment.save()

        return newComment
        
    #
    # Parameters:
    #
    # comment: comment's pk.
    # content: the answer's content.
    # user: GnumaUser object
    #
    @staticmethod
    def create_answer(*args, **kwargs):
        try:
            comment_pk = kwargs['comment']
            user = GnumaUser.objects.get(user = kwargs['user'])
            content = kwargs['content']
            comment = Comment.objects.get(pk = comment_pk)
        except KeyError:
            raise
        except Comment.DoesNotExist:
            raise

        instance = {'content' : content, 'parent' : comment_pk, 'user' : user}
        answer = CommentSerializer(data = instance)

        try:
            answer.is_valid(raise_exception = True)
        except Exception:
            raise

        instance['parent'] = comment
        newAnswer = Comment.objects.create(**instance)
        newAnswer.save()

        return newAnswer

    
    @staticmethod
    def delete(*args, **kwargs):
        try:
            comment_pk = kwargs['comment']
            comment = Comment.objects.get(pk = comment_pk)
        except KeyError:
            raise
        except Comment.DoesNotExist:
            raise
        
        comment.delete()
        return True

    
    @staticmethod
    def edit(*args, **kwargs):
        try:
            comment_pk = kwargs['comment']
            content = kwargs['content']
            comment = Comment.objects.get(pk = comment_pk)
        except KeyError:
            raise
        except Comment.DoesNotExist:
            raise
        
        instance = {'content' : content}
        check = CommentSerializer(data = instance)

        try:
            check.is_valid(raise_exception = True)
        except Exception:
            raise
        
        comment.content = content
        comment.is_edit = True
        comment.save()

        return True

    #
    # Parameters:
    #
    # comment: comment's pk
    # content: the report's comment
    # user: GnumaUser object
    #
    @staticmethod
    def report(*args, **kwargs):
        try:
            comment_pk = kwargs['comment']
            content = kwargs['content']
            user = GnumaUser.objects.get(user = kwargs['user'])
            comment = Comment.objects.get(pk = comment_pk)
        except KeyError:
            raise
        except Comment.DoesNotExist:
            raise

        #
        # A user can report a comment only once.
        #
        try:
            Report.objects.get(sender = user, comment = comment)
            return False
        except Report.DoesNotExist:
            #
            # is_valid should be added.
            #
            new_report = Report(sender = user, comment = comment, content = content)
            new_report.save()
            return True