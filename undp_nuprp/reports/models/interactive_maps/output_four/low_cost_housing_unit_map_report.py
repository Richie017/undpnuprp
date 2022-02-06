from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.models.base.base import Report

__author__ = 'Kaikobud'


@decorate(is_object_context,
          route(route='low-cost-housing-unit-map', group=' Housing Finance ', item_order=2, group_order=4,
                module=ModuleEnum.InteractiveMap, display_name="Number of Low-Cost Housing Units"))
class LowCostHousingUnitMapReport(Report):
    class Meta:
        proxy = True
