from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity


__author__ = 'Mahmud'

# @decorate(save_audit_log, route(route='filters', hide=True, display_name='Filter'))
class QueryFilter(OrganizationDomainEntity):
    context = models.CharField(max_length=200, default='')
