from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.managers.not_done_manager import get_blank_report_data
from undp_nuprp.reports.models.base.base import Report

__author__ = 'Ashraful'


@decorate(is_object_context,
          route(route='o-and-m-funds', group='Infrastructure & Urban Services ', group_order=5,
                module=ModuleEnum.Reports,
                display_name="O&M Funds", item_order=3))
class OAndMFundsReport(Report):
    class Meta:
        proxy = True
        app_label = 'reports'

    def build_report(self, wards=list(), from_time=None, to_time=None, indicator=None, graph_type=None):
        return get_blank_report_data()
