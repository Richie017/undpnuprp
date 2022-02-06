from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.users.user import ConsoleUser

__author__ = 'ruddra'

from django.db import models


class SessionKey(OrganizationDomainEntity):
    ses_key = models.CharField(max_length=300, null=False)
    user = models.ForeignKey(ConsoleUser, default=None)
    context = models.CharField(max_length=8000, null=True, default='')