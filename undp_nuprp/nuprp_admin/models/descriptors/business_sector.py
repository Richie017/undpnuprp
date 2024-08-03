from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.nuprp_admin.models.descriptors.sector import Sector

__author__ = 'Ziaul Haque'


@decorate(is_object_context,
          route(route='business-sector', group='Descriptors',
                module=ModuleEnum.Settings, display_name="Business Sector", item_order=1))
class BusinessSector(Sector):
    class Meta:
        proxy = True
        app_label = 'nuprp_admin'
