__author__ = 'ruddra'
from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity


class ExporterColumnConfig(OrganizationDomainEntity):
    column = models.IntegerField(default=0)
    column_name = models.CharField(default='', max_length=200)
    property_name = models.CharField(default='', max_length=500)
    ignore = models.BooleanField(default=0)
    children = models.ManyToManyField('self', symmetrical=False)
