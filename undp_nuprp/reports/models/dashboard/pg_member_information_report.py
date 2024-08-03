from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.managers.pg_member.pg_hh_number_indicator import get_pg_hh_status_indicator_pie_chart_data, \
    get_pg_hh_status_indicator_table_data, get_pg_hh_status_indicator_flat_data
from undp_nuprp.reports.managers.pg_member.pg_member_age_indicator import get_pgage_indicator_table_data, \
    get_pgage_indicator_pie_chart_data
from undp_nuprp.reports.managers.pg_member.pg_member_disability_indicator import \
    get_disability_status_indicator_pie_chart_data, get_disability_status_indicator_table_data, \
    get_disability_status_indicator_bar_chart_data
from undp_nuprp.reports.managers.pg_member.pg_member_education_indicator import \
    get_pg_education_attainment_indicator_pie_chart_data, get_pg_education_attainment_indicator_table_data
from undp_nuprp.reports.managers.pg_member.pg_member_employment_indicator import \
    get_pg_employment_status_indicator_table_data, get_pg_employment_status_indicator_pie_chart_data
from undp_nuprp.reports.managers.pg_member.pg_member_ethnicity_indicator import \
    get_pgethnicity_indicator_pie_chart_data, get_pgethnicity_indicator_table_data
from undp_nuprp.reports.managers.pg_member.pg_member_gender_indicator import get_pggender_indicator_table_data, \
    get_pg_gender_indicator_pie_chart_data
from undp_nuprp.reports.managers.pg_member.pg_member_marital_status_indicator import \
    get_pgmarital_status_indicator_pie_chart_data, get_pgmarital_status_indicator_table_data
from undp_nuprp.reports.managers.pg_member.pg_member_religion_indicator import get_pgreligion_indicator_table_data, \
    get_pgreligion_indicator_pie_chart_data
from undp_nuprp.reports.managers.pg_member.pg_number_indicator import get_pgnumber_indicator_pie_chart_data, \
    get_pgnumber_indicator_table_data, get_pgnumber_indicator_flat_data
from undp_nuprp.reports.models.base.base import Report
from undp_nuprp.reports.utils.enums.graph_types import DataTableConfigEnum, GraphTypeEnum
from undp_nuprp.reports.utils.enums.pg_member_indicator import PGMemberIndicatorEnum

__author__ = "Shama"


@decorate(is_object_context,
          route(route='pg-member-information-indicators', group='Local Economy Livelihood and Financial Inclusion ',
                group_order=3,
                module=ModuleEnum.Reports,
                display_name="PG Member Information", item_order=1))
class PGMemberInformationReport(Report):
    class Meta:
        proxy = True
        app_label = 'reports'

    def build_report(self, wards=list(), from_time=None, to_time=None, indicator=None, graph_type=None):

        if indicator == PGMemberIndicatorEnum.PGNumberEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_pgnumber_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_pgnumber_indicator_pie_chart_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_pgnumber_indicator_flat_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == PGMemberIndicatorEnum.PGGenderEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_pggender_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_pg_gender_indicator_pie_chart_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == PGMemberIndicatorEnum.PGReligionEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_pgreligion_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_pgreligion_indicator_pie_chart_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == PGMemberIndicatorEnum.PGEthnicityEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_pgethnicity_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_pgethnicity_indicator_pie_chart_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == PGMemberIndicatorEnum.PGMaritalStatusEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_pgmarital_status_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_pgmarital_status_indicator_pie_chart_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == PGMemberIndicatorEnum.PGEmploymentEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_pg_employment_status_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_pg_employment_status_indicator_pie_chart_data(wards=wards, from_time=from_time,
                                                                         to_time=to_time)

        if indicator == PGMemberIndicatorEnum.PGEducationEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_pg_education_attainment_indicator_table_data(wards=wards, from_time=from_time,
                                                                        to_time=to_time)
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_pg_education_attainment_indicator_pie_chart_data(wards=wards, from_time=from_time,
                                                                            to_time=to_time)

        if indicator == PGMemberIndicatorEnum.PGHHEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_pg_hh_status_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_pg_hh_status_indicator_pie_chart_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_pg_hh_status_indicator_flat_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == PGMemberIndicatorEnum.PGDisabilityEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_disability_status_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_disability_status_indicator_pie_chart_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == GraphTypeEnum.StackedBarChart.value:
                return get_disability_status_indicator_bar_chart_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == PGMemberIndicatorEnum.PGAgeEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_pgage_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_pgage_indicator_pie_chart_data(wards=wards, from_time=from_time, to_time=to_time)
