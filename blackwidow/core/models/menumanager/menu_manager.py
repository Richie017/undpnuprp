from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'Shamil on 09-Mar-16 1:22 PM'


@decorate(
    is_object_context,
    route(route='menu-manager', display_name='Menu Manager',
          group='Other Admin', module=ModuleEnum.Settings)
)
class MenuManager(OrganizationDomainEntity):
    class Meta:
        app_label = 'core'
