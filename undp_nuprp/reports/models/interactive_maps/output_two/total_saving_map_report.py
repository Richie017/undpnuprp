from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.models.base.base import Report

__author__ = 'Kaikobud'


@decorate(is_object_context,
          route(route='total-savings-map', group=' Social Mobilization and Community Capacity Building ', item_order=3,
                group_order=2, module=ModuleEnum.InteractiveMap, display_name="Value of Total Savings"))
class TotalSavingMapReport(Report):
    class Meta:
        proxy = True
