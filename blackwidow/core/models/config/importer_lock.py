from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity


__author__ = 'Mahmud'


class ImporterLock(OrganizationDomainEntity):
    model = models.CharField(max_length=200)

