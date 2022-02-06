__author__ = 'Sohel'
from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.extensions.clock import Clock

class TrackModelM2MChangeModel(OrganizationDomainEntity):
    model_name = models.CharField(max_length=100)
    create_time = models.BigIntegerField(default=0)
    modified_time = models.BigIntegerField(default=0)

    def __str__(self):
        return '%s' % (self.model_name)

    def save(self, force_insert=False, force_update=False, using=None,update_fields=None):
        now_time = Clock.timestamp()
        if not self.pk:
            self.create_time = now_time
            self.modified_time = now_time
        else:
            self.modified_time = now_time

        super().save(force_insert=force_insert,force_update=force_update,using=using,update_fields=update_fields)
