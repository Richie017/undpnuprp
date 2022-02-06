"""
Created by tareq on 2/12/18
"""
from django.db import models

from blackwidow.core.models.contracts.base import DomainEntity

__author__ = 'Tareq'


class KeyValueCount(DomainEntity):
    label = models.CharField(max_length=512, blank=True)
    count = models.IntegerField(default=0)

    class Meta:
        app_label = 'reports'
