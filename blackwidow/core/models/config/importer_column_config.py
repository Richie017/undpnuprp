from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity


__author__ = 'Mahmud'


class ImporterColumnConfig(OrganizationDomainEntity):
    column = models.IntegerField(default=0)
    column_name = models.CharField(default='', max_length=200)
    property_name = models.CharField(default='', max_length=500)
    ignore = models.BooleanField(default=0)
    is_unique = models.NullBooleanField(default=False, null=True)
    children = models.ManyToManyField('self', symmetrical=False)

