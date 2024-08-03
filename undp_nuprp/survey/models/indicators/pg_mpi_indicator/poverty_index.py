from blackwidow.core.models.contracts.base import DomainEntity
from django.db import models

from blackwidow.engine.extensions.console_debug import bw_debug

__author__ = 'Tareq'


class PGPovertyIndex(DomainEntity):
    primary_group_member = models.ForeignKey('nuprp_admin.PrimaryGroupMember', null=True)
    index_no = models.IntegerField(default=0)
    index_name = models.CharField(max_length=256, blank=True)
    index_description = models.TextField(blank=True, null=True)
    is_deprived = models.BooleanField(default=True)
    score = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        bw_debug("%s deprives: %d - %s" % (self.primary_group_member.name, self.index_no, self.index_name))
