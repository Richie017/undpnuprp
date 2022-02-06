"""
    Created by tareq on 3/13/17
"""

from undp_nuprp.reports.managers.household_survey.dependent_members_indicator_manager import \
    get_dependent_members_indicator_column_chart_data
from undp_nuprp.reports.managers.household_survey.deprived_household_indicator_manager import \
    get_deprived_household_column_chart_data, get_deprived_household_bar_chart_data, get_deprived_household_table_data
from undp_nuprp.reports.managers.household_survey.education_indicator_manager import \
    get_educational_indicator_pie_chart_data, get_educational_indicator_column_chart_data, \
    get_educational_indicator_table_data
from undp_nuprp.reports.managers.household_survey.employment_indicator_manager import \
    get_employment_indicator_pie_chart_data, get_employment_indicator_column_chart_data, \
    get_employment_indicator_table_data
from undp_nuprp.reports.managers.household_survey.gender_indicator_manager import get_gender_indicator_pie_chart_data, \
    get_gender_indicator_column_chart_data, get_gender_indicator_table_data
from undp_nuprp.reports.managers.household_survey.household_mpi_indicator_manager import \
    get_household_mpi_scatter_chart_data, get_household_mpi_column_chart_data
from undp_nuprp.reports.managers.household_survey.mean_household_size_indicator_manager import \
    get_mean_household_size_data, get_mean_household_size_table_data
from undp_nuprp.reports.managers.household_survey.mpi_vs_characteristic_indicator_manager import \
    get_mpi_vs_characteristic_indicator_column_chart_data
from undp_nuprp.reports.models.base.base import Report

from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.utils.enums.graph_types import GraphTypeEnum, DataTableConfigEnum
from undp_nuprp.reports.utils.enums.household_survey_indicator import HouseholdSurveyIndicatorEnum

__author__ = 'Tareq'


@decorate(is_object_context,
          route(route='hh-survey-indicators', group='Household Information', group_order=7,
                module=ModuleEnum.Reports, display_name="Household Survey Indicators", item_order=1))
class HouseholdSurveyIndicatorReport(Report):
    class Meta:
        proxy = True
        app_label = 'reports'

    def build_report(self, wards=list(), from_time=None, to_time=None, indicator=None, graph_type=None):
        if indicator == HouseholdSurveyIndicatorEnum.GenderIndicator.value:
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_gender_indicator_pie_chart_data(wards=wards, from_time=from_time, to_time=to_time)
            elif graph_type == GraphTypeEnum.StackedColumnChart.value:
                return get_gender_indicator_column_chart_data(wards=wards, from_time=from_time, to_time=to_time)
            elif graph_type == DataTableConfigEnum.DataTable.value:
                return get_gender_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == HouseholdSurveyIndicatorEnum.EmploymentIndicator.value:
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_employment_indicator_pie_chart_data(wards=wards, from_time=from_time, to_time=to_time)
            elif graph_type == GraphTypeEnum.StackedColumnChart.value:
                return get_employment_indicator_column_chart_data(wards=wards, from_time=from_time, to_time=to_time)
            elif graph_type == DataTableConfigEnum.DataTable.value:
                return get_employment_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == HouseholdSurveyIndicatorEnum.EducationalIndicator.value:
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_educational_indicator_pie_chart_data(wards=wards, from_time=from_time, to_time=to_time)
            elif graph_type == GraphTypeEnum.StackedColumnChart.value:
                return get_educational_indicator_column_chart_data(wards=wards, from_time=from_time, to_time=to_time)
            elif graph_type == DataTableConfigEnum.DataTable.value:
                return get_educational_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == HouseholdSurveyIndicatorEnum.DependentMemberIndicator.value:
            if graph_type == GraphTypeEnum.StackedColumnChart.value:
                return get_dependent_members_indicator_column_chart_data(wards=wards, from_time=from_time,
                                                                         to_time=to_time)

        if indicator == HouseholdSurveyIndicatorEnum.HouseholdSizeIndicator.value:
            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_mean_household_size_data(wards=wards, from_time=from_time,
                                                    to_time=to_time)
            elif graph_type == DataTableConfigEnum.DataTable.value:
                return get_mean_household_size_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == HouseholdSurveyIndicatorEnum.HouseholdMPIIndicator.value:
            if graph_type == GraphTypeEnum.ScatterChart.value:
                return get_household_mpi_scatter_chart_data(wards=wards, from_time=from_time,
                                                            to_time=to_time)
            if graph_type == GraphTypeEnum.StackedColumnChart.value:
                return get_household_mpi_column_chart_data(wards=wards, from_time=from_time,
                                                           to_time=to_time)

        if indicator == HouseholdSurveyIndicatorEnum.DeprivedHouseholdIndicator.value:
            if graph_type == GraphTypeEnum.StackedColumnChart.value:
                return get_deprived_household_column_chart_data(wards=wards, from_time=from_time,
                                                                to_time=to_time)
            if graph_type == GraphTypeEnum.HorizontalBarChart.value:
                return get_deprived_household_bar_chart_data(wards=wards, from_time=from_time,
                                                             to_time=to_time)
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_deprived_household_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == HouseholdSurveyIndicatorEnum.MPIvsCharacteristicIndicator.value:
            if graph_type == GraphTypeEnum.ColumnChart.value:
                return get_mpi_vs_characteristic_indicator_column_chart_data(wards=wards, from_time=from_time,
                                                                             to_time=to_time)
