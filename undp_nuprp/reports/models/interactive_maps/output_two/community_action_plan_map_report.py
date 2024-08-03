from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.models.base.base import Report

__author__ = 'Kaikobud'


@decorate(is_object_context,
          route(route='community-action-plan-map', group=' Social Mobilization and Community Capacity Building ',
                item_order=1, group_order=2, module=ModuleEnum.InteractiveMap,
                display_name="Number of Community Action Plan"))
class CommunityActionPlanMapReport(Report):
    class Meta:
        proxy = True
