from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'ruddra'

from django.db import models


class SearchResult(OrganizationDomainEntity):
    name = models.CharField(max_length=255, null=True, default=None)
    description = models.CharField(max_length=255, null=True, default=None)
    url = models.CharField(max_length=255, null=True, default=None)
