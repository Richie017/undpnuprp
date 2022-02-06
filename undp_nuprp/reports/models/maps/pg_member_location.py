from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.models.base.base import Report

__author__ = 'Tareq'


@decorate(is_object_context,
          route(route='pg-member-location-map', group='Maps', item_order=4, group_order=11,
                module=ModuleEnum.Reports, display_name="PG Member Registration Location"))
class PGMemberLocationReport(Report):
    class Meta:
        proxy = True
