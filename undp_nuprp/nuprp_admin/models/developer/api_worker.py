from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'shamil'


@decorate(
    is_object_context,
    route(route='api-worker', display_name='API Worker', group='Other Admin',
          module=ModuleEnum.Settings, group_order=2, item_order=10)
)
class APIWorker(OrganizationDomainEntity):

    @classmethod
    def get_manage_buttons(cls):
        return []

    class Meta:
        app_label = 'core'
