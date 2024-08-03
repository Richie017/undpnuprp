from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.models.base.base import Report

__author__ = 'Ziaul Haque'


@decorate(is_object_context,
          route(route='crmif-interventions-map', group=' Infrastructure & Urban Services ', item_order=2,
                group_order=5, module=ModuleEnum.InteractiveMap, display_name="CRMIF Interventions"))
class CRMIFInterventionMapReport(Report):
    class Meta:
        proxy = True
