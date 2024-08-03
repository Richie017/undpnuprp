from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.managers.pg_hh_head.pg_hh_head_disability_indicator import \
    get_hh_head_disability_status_indicator_table_data, get_hh_head_disability_status_indicator_pie_chart_data, \
    get_hh_head_disability_status_indicator_bar_chart_data
from undp_nuprp.reports.managers.pg_hh_head.pg_hh_head_education_indicator import \
    get_hh_head_education_attainment_indicator_pie_chart_data, get_hh_head_education_attainment_indicator_table_data
from undp_nuprp.reports.managers.pg_hh_head.pg_hh_head_employment_indicator import \
    get_hh_head_employment_status_indicator_table_data, get_hh_head_employment_status_indicator_pie_chart_data
from undp_nuprp.reports.managers.pg_hh_head.pg_hh_head_gender_indicator import get_hhgender_indicator_pie_chart_data, \
    get_hhgender_indicator_table_data
from undp_nuprp.reports.models.base.base import Report
from undp_nuprp.reports.utils.enums.graph_types import DataTableConfigEnum, GraphTypeEnum
from undp_nuprp.reports.utils.enums.pg_hh_head_indicator import PGHHHeadIndicatorEnum

__author__ = "Shama, Ziaul Haque"


@decorate(is_object_context,
          route(route='pg-hh-head-information-indicators', group='Local Economy Livelihood and Financial Inclusion ',
                group_order=3,
                module=ModuleEnum.Reports,
                display_name="PG HH Head Information", item_order=2))
class PGHHHeadInformationReport(Report):
    class Meta:
        proxy = True
        app_label = 'reports'

    def build_report(self, wards=list(), from_time=None, to_time=None, indicator=None, graph_type=None):
        if indicator == PGHHHeadIndicatorEnum.HHHeadGenderEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_hhgender_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_hhgender_indicator_pie_chart_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == PGHHHeadIndicatorEnum.HHHeadEmploymentEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_hh_head_employment_status_indicator_table_data(wards=wards, from_time=from_time,
                                                                          to_time=to_time)
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_hh_head_employment_status_indicator_pie_chart_data(wards=wards, from_time=from_time,
                                                                              to_time=to_time)

        if indicator == PGHHHeadIndicatorEnum.HHHeadEducationEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_hh_head_education_attainment_indicator_table_data(wards=wards, from_time=from_time,
                                                                             to_time=to_time)
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_hh_head_education_attainment_indicator_pie_chart_data(wards=wards, from_time=from_time,
                                                                                 to_time=to_time)

        if indicator == PGHHHeadIndicatorEnum.HHHeadDisabilityEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_hh_head_disability_status_indicator_table_data(
                    wards=wards, from_time=from_time, to_time=to_time
                )
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_hh_head_disability_status_indicator_pie_chart_data(
                    wards=wards, from_time=from_time, to_time=to_time
                )
            if graph_type == GraphTypeEnum.StackedBarChart.value:
                return get_hh_head_disability_status_indicator_bar_chart_data(
                    wards=wards, from_time=from_time, to_time=to_time
                )
