from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.managers.pg_hh_information.pg_hh_composition_indicator import \
    get_hh_composition_indicator_table_data
from undp_nuprp.reports.managers.pg_hh_information.pg_hh_dependents_indicator import \
    get_hhdependent_members_indicator_column_chart_data
from undp_nuprp.reports.managers.pg_hh_information.pg_hh_deprived_indicator import get_deprived_pghh_table_data, \
    get_deprived_pghh_bar_chart_data
from undp_nuprp.reports.managers.pg_hh_information.pg_hh_mean_indicator import get_mean_pghh_size_table_data, \
    get_mean_pghh_size_flat_data
from undp_nuprp.reports.managers.pg_hh_information.pg_hh_mpi_vs_hh_indicator import \
    get_pghh_mpi_vs_characteristic_indicator_column_chart_data, get_pghh_mpi_vs_characteristic_indicator_table_data
from undp_nuprp.reports.managers.pg_hh_information.pg_hh_vulnerability_indicator import get_pghh_mpi_column_chart_data, \
    get_pghh_mpi_table_data
from undp_nuprp.reports.models.base.base import Report
from undp_nuprp.reports.utils.enums.graph_types import GraphTypeEnum, DataTableConfigEnum
from undp_nuprp.reports.utils.enums.pg_hh_indicator import PGHHIndicatorEnum

__author__ = "Shama"


@decorate(is_object_context,
          route(route='pg-hh-information-indicators', group='Local Economy Livelihood and Financial Inclusion ',
                group_order=3,
                module=ModuleEnum.Reports,
                display_name="PG HH Information", item_order=3))
class PGHHInformationReport(Report):
    class Meta:
        proxy = True
        app_label = 'reports'

    def build_report(self, wards=list(), from_time=None, to_time=None, indicator=None, graph_type=None):
        if indicator == PGHHIndicatorEnum.HHDependentsEnum.value:
            if graph_type == GraphTypeEnum.StackedColumnChart.value:
                return get_hhdependent_members_indicator_column_chart_data(wards=wards, from_time=from_time,
                                                                           to_time=to_time)
        if indicator == PGHHIndicatorEnum.HHMeanSizeEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_mean_pghh_size_table_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_mean_pghh_size_flat_data(wards=wards, from_time=from_time, to_time=to_time)
        if indicator == PGHHIndicatorEnum.HHDeprivationEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_deprived_pghh_table_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == GraphTypeEnum.HorizontalBarChart.value:
                return get_deprived_pghh_bar_chart_data(wards=wards, from_time=from_time, to_time=to_time)
        if indicator == PGHHIndicatorEnum.HHVulnerabilityEnum.value:
            if graph_type == GraphTypeEnum.ColumnChart.value:
                return get_pghh_mpi_column_chart_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_pghh_mpi_table_data(wards=wards, from_time=from_time, to_time=to_time)
        if indicator == PGHHIndicatorEnum.MPICharacteristicsEnum.value:
            if graph_type == GraphTypeEnum.StackedColumnChart.value:
                return get_pghh_mpi_vs_characteristic_indicator_column_chart_data(
                    wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_pghh_mpi_vs_characteristic_indicator_table_data(
                    wards=wards, from_time=from_time, to_time=to_time)
        if indicator == PGHHIndicatorEnum.HHCompositionEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_hh_composition_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)
