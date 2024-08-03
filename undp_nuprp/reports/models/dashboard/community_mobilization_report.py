"""
    Created by tareq on 3/13/17
"""

from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.managers.community_mobilization.cdc_cluster_number_registered_indicator import \
    get_cdc_cluster_registered_indicator_flat_data, get_cdc_cluster_registered_indicator_table_data
from undp_nuprp.reports.managers.community_mobilization.cdc_number_registered_indicator import \
    get_cdc_number_registered_indicator_flat_data, get_cdc_number_registered_indicator_table_data
from undp_nuprp.reports.managers.community_mobilization.pg_member_registered_indicator import \
    get_pg_member_registered_indicator_flat_data, get_pg_member_registered_indicator_table_data
from undp_nuprp.reports.managers.community_mobilization.pg_number_registered_indicator import \
    get_pg_number_registered_indicator_table_data, get_pg_number_registered_indicator_flat_data
from undp_nuprp.reports.managers.not_done_manager import get_blank_report_data
from undp_nuprp.reports.models.base.base import Report
from undp_nuprp.reports.utils.enums.community_mobilization_indicator import CommunityMobilizationIndicatorEnum
from undp_nuprp.reports.utils.enums.graph_types import GraphTypeEnum, DataTableConfigEnum

__author__ = 'Tareq'


@decorate(is_object_context,
          route(route='community-mobilization-indicators', group='Community Mobilization', group_order=5, module=ModuleEnum.Reports,
                display_name="Community Mobilization", item_order=9, hide=True))
class CommunitiMobilizationReport(Report):
    class Meta:
        proxy = True
        app_label = 'reports'

    def build_report(self, wards=list(), from_time=None, to_time=None, indicator=None, graph_type=None):
        if indicator == CommunityMobilizationIndicatorEnum.PGMemberEnum.value:
            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_pg_member_registered_indicator_flat_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_pg_member_registered_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == CommunityMobilizationIndicatorEnum.PGNumberEnum.value:
            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_pg_number_registered_indicator_flat_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_pg_number_registered_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == CommunityMobilizationIndicatorEnum.CDCNumberEnum.value:
            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_cdc_number_registered_indicator_flat_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_cdc_number_registered_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == CommunityMobilizationIndicatorEnum.CDCClusterNumberEnum.value:
            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_cdc_cluster_registered_indicator_flat_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_cdc_cluster_registered_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)
        if indicator == CommunityMobilizationIndicatorEnum.AllPGMemberEnum.value:
            return get_blank_report_data()
        if indicator == CommunityMobilizationIndicatorEnum.AllPGNumberEnum.value:
            return get_blank_report_data()
        if indicator == CommunityMobilizationIndicatorEnum.AllCDCNumberEnum.value:
            return get_blank_report_data()
        if indicator == CommunityMobilizationIndicatorEnum.AllCDCClusterNumberEnum.value:
            return get_blank_report_data()