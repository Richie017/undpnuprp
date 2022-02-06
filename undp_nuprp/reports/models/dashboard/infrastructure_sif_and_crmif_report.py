from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.managers.not_done_manager import get_blank_report_data
from undp_nuprp.reports.models.base.base import Report

__author__ = 'Ashraful'


@decorate(is_object_context,
          route(route='infrastructure-sif-and-crmif', group='Infrastructure(SIF & CRMIF)', group_order=9,
                module=ModuleEnum.Reports, display_name="Infrastructure(SIF & CRMIF)", item_order=10, hide=True))
class InfrastructureSIFAndCRMIFReport(Report):
    # The following model is deprecated. SIFReport and CRMIFReport models are brought and currently in use

    class Meta:
        proxy = True
        app_label = 'reports'

    def build_report(self, wards=list(), from_time=None, to_time=None, indicator=None, graph_type=None):
        return get_blank_report_data()
