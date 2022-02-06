"""
    Created by tareq on 3/13/17
"""

from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.managers.cdc_performance.cdc_performance_indicator import \
    get_cdc_performance_indicator_table_data_1
from undp_nuprp.reports.models.base.base import Report

__author__ = 'Tareq, Kaikobud'

from undp_nuprp.reports.utils.enums.graph_types import DataTableConfigEnum


@decorate(is_object_context,
          route(route='cdc-performance-indicators', group='Social Mobilization and Community Capacity Building ',
                group_order=2, module=ModuleEnum.Reports,
                display_name="CDC Performance", item_order=2))
class CDCPerformanceReport(Report):
    class Meta:
        proxy = True
        app_label = 'reports'

    def build_report(self, graph_type=None, year=None):
        if graph_type == DataTableConfigEnum.DataTable.value + '1':
            return get_cdc_performance_indicator_table_data_1(year)
