import json
from .models import Notification
from .serializers import NotificationSerializer

#
# This class handles the notification.
#
class NotificationHandler(object):

    #
    # This method save a notification into the database.
    #
    # Parameters (kwargs):
    # - data : notification's data. (must be __dict__)
    # - destination: destination user.
    # - item : item's pk.
    #
    # It returns 1 on success and 0 on failure.
    #
    @staticmethod
    def save(**kwargs):
        if 'data' not in kwargs or 'destination' not in kwargs or 'item' not in kwargs:
            return 0

        if kwargs['data']['type'] not in Notification.TYPES:
            return 0

        try:
            data = json.dumps(kwargs['data'])
        except Exception as e:
            print('ERRORE OCCURED WHILE SAVING A NOTIFICATION: %s' % str(e))
            return 0
        
        instance = {'destination' : kwargs['destination'], 'notification' : data, 'item' : kwargs['item']}
        serializer = NotificationSerializer(data = instance)

        try:
            serializer.is_valid(raise_exception = True)
        except Exception as e:
            print('ERRORE OCCURED WHILE SAVING A NOTIFICATION: %s' % str(e))
            return 0
        
        serializer.save()
        return 1
    
    #
    # This method retrieves all the notifications related to an user.
    #  
    # Parameters (kwargs):
    # - user : Django User object.
    #
    # It returns array on success and 0 on failure.
    #
    @staticmethod
    def retrieve(**kwargs):
        if 'user' not in kwargs:
            return 0

        data = Notification.objects.filter(destination = kwargs['user']) # order by createdAt
        response = {}
        response['notifications'] = []
        for n in data:
            response['notifications'].append(json.loads(n.notification))
            n.delete()  # ??
        
        return response

    #
    # For now, this method just deletes all the notification 
    # related to the given parameters.
    #
    # Parameters(kwargs):
    # - user : destination.
    # - item : item related to the notification.
    #
    # It returns 1 on success and 0 on failure.
    #
    @staticmethod
    def delete(**kwargs):
        if 'user' not in kwargs or 'item' not in kwargs:
            return 0

        toDelete = Notification.objects.filter(destination = kwargs['user'], item = kwargs['item'])

        for notification in toDelete:
            notification.delete()

        return 1
