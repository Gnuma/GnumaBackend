# django imports
from django.db.models import Q, Max

# local imports
from .models import ItemAccess
from gnuma.models import Ad, Comment, GnumaUser

#
# Anytime a user access to an item this class takes care of registering it.
#
class BaseProfiling(object):

    @staticmethod
    def createAccess(*args, **kwargs):
        try:
            item = kwargs['item']
            user = GnumaUser.objects.get(user = kwargs['user'])       # User object there's no need to check it
        except KeyError:
            raise
        
        register = ItemAccess(item = item, owner = user)
        register.save()

        return True


    #
    # Unlike the other methods, the 'user' key is a GnumaUser's instance
    #
    @staticmethod
    def hasany(*args, **kwargs):
        try:
            item = kwargs['item']
            user = kwargs['user']
        except KeyError:
            raise

        try:
            ItemAccess.objects.get(owner = user, item = item)
        except ItemAccess.DoesNotExist:
            return False
        
        return True


    @staticmethod
    def lastAccess(*args, **kwargs):
        try:
            item = kwargs['item']
            user = GnumaUser.objects.get(user = kwargs['user'])
        except KeyError:
            raise

        instance = {'item' : item, 'user' : user}
        if not BaseProfiling.hasany(**instance):
            return False

        access = ItemAccess.objects.get(item = item, owner = user)
        return access.lastAccess


    @staticmethod
    def update(*args, **kwargs):
        try:
            item = kwargs['item']
            user = GnumaUser.objects.get(user = kwargs['user'])
        except KeyError:
            raise

        instance = {'item' : item, 'user' : user}
        if not BaseProfiling.hasany(**instance):
            return False

        access = ItemAccess.objects.get(item = item, owner = user)
        # just update the lastAccess field
        access.save() 
        return True


    @staticmethod
    def anynew(*args, **kwargs):
        try:
            user = GnumaUser.objects.get(user = kwargs['user'])
        except KeyError:
            raise
        
        #
        # Check user's items
        #
        pks = Ad.objects.filter(user = user)
        my_comments = {}
        for pk in pks:
            pk_access = ItemAccess.objects.get(item = pk)
            comment = Comment.objects.filter(item = pk).aggregate(Max('updated'))
            
            if comment.updated__max > pk_access.lastAccess:
                my_comments[pk] = Comment.objects.filter(item = pk).filter(updated = comment.updated__max)

        #
        # Check other items
        #
        accesses = ItemAccess.objects.filter(owner = user).exclude(~Q(item__seller = user))
        other_comments = {}
        for a in accesses:
            last_update = Comment.objects.filter(item = a.item).aggregate(Max('updated'))
            if a.lastAccess < last_update.updated__max:
                #
                #  If the last access is older than the last comment it means that this item needs to be notified.
                #
                other_comments[a.item.pk] = Comment.objects.filter(item = a.item).filter(updated = last_update.updated__max)
        
        if not my_comments and not other_comments:
            return False
        return [my_comments, other_comments]
