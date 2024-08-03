from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity


__author__ = 'ruddra'

# @decorate(is_object_context, route(route='alert-group', display_name='Alert Group',
# module=ModuleEnum.Administration, group='Alerts'))
class AlertGroup(OrganizationDomainEntity):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=2000, null=True, default=None)

    def __str__(self):
        return self.name