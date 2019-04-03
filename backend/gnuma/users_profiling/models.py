#
# This file contains the basic profiling-system model.
#

# django imports
from django.db import models

# local imports 
from gnuma.models import GnumaUser, Ad

class ItemAccess(models.Model):
    owner = models.ForeignKey(GnumaUser, on_delete = models.CASCADE)
    item = models.ForeignKey(Ad, on_delete = models.CASCADE)
    lastAccess = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.item.__str__()+" "+str(self.lastAccess)