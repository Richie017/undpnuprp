from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.models.base.base import Report

__author__ = 'Kaikobud'


@decorate(is_object_context,
          route(route='poverty-conditions-map', group=' Planning and Urban Governance ', item_order=1,
                group_order=1, module=ModuleEnum.InteractiveMap,
                display_name="Poverty conditions of the urban poor settlements"))
class PovertyConditionMapReport(Report):
    class Meta:
        proxy = True
