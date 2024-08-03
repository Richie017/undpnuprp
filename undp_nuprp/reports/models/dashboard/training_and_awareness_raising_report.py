from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.managers.not_done_manager import get_blank_report_data
from undp_nuprp.reports.models.base.base import Report

__author__ = 'Ashraful'


@decorate(is_object_context,
          route(route='training-and-awareness-raising', group='Training and Awareness Raising',
                group_order=6, module=ModuleEnum.Reports,
                display_name="Training and Awareness Raising", item_order=1))
class TrainingAndAwarenessRaisingReport(Report):
    class Meta:
        proxy = True
        app_label = 'reports'

    def build_report(self, wards=list(), from_time=None, to_time=None, indicator=None, graph_type=None):
        return get_blank_report_data()
