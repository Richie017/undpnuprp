"""
    Created by tareq on 3/13/17
"""
from django.db import models
from blackwidow.core.models.activity.periodic_activity import PeriodicBackgroundActivity


__author__ = 'Tareq'


class CacheBase(PeriodicBackgroundActivity):
    object_id = models.IntegerField(default=0)

    class Meta:
        abstract = True

    @classmethod
    def get_drilldown_pivot_field(cls):
        """
        This method returns the field, which will act as the pivot of drilldown of report using this cache.
        :return: the pivot field
        """
        return None
