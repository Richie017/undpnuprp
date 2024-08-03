from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'ruddra'


# @decorate(is_object_context, route(route='email-template', display_name='Email Template',
# module=ModuleEnum.Settings, group='Email Templates'))
class EmailTemplate(OrganizationDomainEntity):
    name = models.CharField(max_length=255)
    content_structure = models.CharField(max_length=2000)

    def __str__(self):
        return self.name
