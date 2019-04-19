#
#  This file contains the comments' subsystem.
#

# Channels imports
from channels.layers import get_channel_layer

# asgiref imports
from asgiref.sync import async_to_sync

# local imports
from gnuma.models import Comment, Ad, Report, GnumaUser
from gnuma.chat.models import Client
from gnuma.serializers import CommentSerializer, AdSerializer
from gnuma.chat.serializers import NotificationAnswerSerializer, NotificationCommentSerializer

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

        #
        # Issue the notification to the item's owner only if
        # the user who's creating this comment is not him.
        #
        if user != item.seller:
            #
            # Build the notification data
            #
            data = {}
            data['type'] = 'newComment'
            data['comment'] = NotificationCommentSerializer(newComment).data
            try:
                channel_name = Client.objects.get(user = item.seller.user).channel_name
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.send)(channel_name, {"type" : "notification.send", "content" : data})
            except Client.DoesNotExist:
                #
                # The user is not online.
                # Just insert the notification into the database.
                #
                # To be implemented
                pass

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

        #
        # Only the item's owner and the comment's owner can 
        # insert answers below this comment.
        #
        if comment.user != user and comment.item.seller != user:
            raise Exception

        instance = {'content' : content, 'parent' : comment_pk, 'user' : user}
        answer = CommentSerializer(data = instance)

        try:
            answer.is_valid(raise_exception = True)
        except Exception:
            raise

        instance['parent'] = comment
        newAnswer = Comment.objects.create(**instance)
        newAnswer.save()

        #
        # Issue the notification depending upon the sender.
        #
        data = {}
        data['type'] = 'newAnswer'
        if comment.user != user:
            data['for'] = 'shopping'
            destination = comment.user.user
        else:
            data['for'] = 'sale'
            destination = comment.item.seller.user
        data['answer'] = NotificationAnswerSerializer(newAnswer).data
        try:
            channel_name = Client.objects.get(user = destination).channel_name
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.send)(channel_name, {"type" : "notification.send", "content" : data})
        except Client.DoesNotExist:
            #
            # The user is not online.
            # Just insert the notification into the database.
            #
            # To be implemented
            pass

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