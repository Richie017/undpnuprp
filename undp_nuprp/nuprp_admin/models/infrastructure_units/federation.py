from blackwidow.core.models.structure.infrastructure_unit import InfrastructureUnit
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = "Shama"


@decorate(is_object_context,
          route(route='federation', group='Social Mobilization and Community Capacity Building',
                module=ModuleEnum.Analysis,
                display_name='Federation', group_order=2, item_order=11))
class Federation(InfrastructureUnit):
    class Meta:
        app_label = 'nuprp_admin'
        proxy = True
