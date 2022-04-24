"""
    Created by tareq on 3/13/17
"""

from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.managers.socio_economic_fund.age_distribution_of_grantees import \
    get_age_distributor_of_grantees_table_data, get_age_distributor_of_grantees_pie_chart_data
from undp_nuprp.reports.managers.socio_economic_fund.disability_status_of_grantee_indicator import \
    get_disability_status_of_grantee_stack_bar_chart_data, get_disability_status_of_grantee_data_table_data, \
    get_disability_status_of_grantee_pie_chart_data
from undp_nuprp.reports.managers.socio_economic_fund.gender_of_grantees import \
    get_gender_of_grantee_table_data, get_gender_of_grantee_pie_chart_data
from undp_nuprp.reports.managers.socio_economic_fund.grantees_indicator_manager import \
    get_grantees_education_indicator_table_data, get_grantees_mpi_indicator_table_data
from undp_nuprp.reports.managers.socio_economic_fund.number_of_grantees import \
    get_number_of_grantees_indicator_table_data, get_number_of_grantees_indicator_column_chart_data
from undp_nuprp.reports.managers.socio_economic_fund.type_of_business_of_business_grantee import \
    get_type_of_business_of_business_grantee_table_data, get_type_of_business_of_business_grantee_pie_chart_data
from undp_nuprp.reports.managers.socio_economic_fund.type_of_trades_of_apprenticeship_grantees import \
    get_type_of_trading_of_apprenticeship_grantee_table_data, \
    get_type_of_trading_of_apprenticeship_grantee_pie_chart_data
from undp_nuprp.reports.managers.socio_economic_fund.value_of_grantee_indicator import \
    get_value_of_grantee_indicator_table_data, get_value_of_grantee_indicator_column_chart_data, \
    get_value_of_grantee_indicator_column_flat_data
from undp_nuprp.reports.managers.socio_economic_fund.grantees_by_ward_prioritization_index import \
    get_grantees_by_ward_prioritization_index_table_data

from undp_nuprp.reports.models.base.base import Report
from undp_nuprp.reports.utils.enums.graph_types import DataTableConfigEnum, GraphTypeEnum
from undp_nuprp.reports.utils.enums.socio_economic_fund_indicator import SocioEconomicFundIndicatorEnum

__author__ = 'Tareq', 'Shuvro'


@decorate(is_object_context,
          route(route='socio-economic-fund-grant-indicators', group='Local Economy Livelihood and Financial Inclusion ',
                group_order=3,
                module=ModuleEnum.Reports,
                display_name="Socio Economic Fund Grant", item_order=4))
class SocioEconomicFundGrantReport(Report):
    class Meta:
        proxy = True
        app_label = 'reports'

    def build_report(self, towns=list, indicator=None, graph_type=None):
        if indicator == SocioEconomicFundIndicatorEnum.GranteeEnum.value:
            if graph_type == GraphTypeEnum.ColumnChart.value:
                return get_number_of_grantees_indicator_column_chart_data()
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_number_of_grantees_indicator_table_data(towns=towns)

        if indicator == SocioEconomicFundIndicatorEnum.GenderEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_gender_of_grantee_table_data(towns=towns)
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_gender_of_grantee_pie_chart_data()

        if indicator == SocioEconomicFundIndicatorEnum.ApBusinessAreaEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_type_of_trading_of_apprenticeship_grantee_table_data(towns=towns)
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_type_of_trading_of_apprenticeship_grantee_pie_chart_data()

        if indicator == SocioEconomicFundIndicatorEnum.BGBusinessAreaEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_type_of_business_of_business_grantee_table_data(towns=towns)
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_type_of_business_of_business_grantee_pie_chart_data()

        if indicator == SocioEconomicFundIndicatorEnum.EducationIndicatorEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_grantees_education_indicator_table_data(towns=towns)

        if indicator == SocioEconomicFundIndicatorEnum.DisabledIndicatorEnum.value:
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_disability_status_of_grantee_pie_chart_data()
            if graph_type == GraphTypeEnum.StackedBarChart.value:
                return get_disability_status_of_grantee_stack_bar_chart_data()
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_disability_status_of_grantee_data_table_data(towns=towns)

        if indicator == SocioEconomicFundIndicatorEnum.GranteeMPIIndicatorEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_grantees_mpi_indicator_table_data(towns=towns)

        if indicator == SocioEconomicFundIndicatorEnum.AgeIndicatorEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_age_distributor_of_grantees_table_data(towns=towns)
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_age_distributor_of_grantees_pie_chart_data()

        if indicator == SocioEconomicFundIndicatorEnum.ValueOfGranteeIndicatorEnum.value:
            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_value_of_grantee_indicator_column_flat_data(towns=towns)
            if graph_type == GraphTypeEnum.ColumnChart.value:
                return get_value_of_grantee_indicator_column_chart_data()
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_value_of_grantee_indicator_table_data(towns=towns)


        if indicator == SocioEconomicFundIndicatorEnum.GranteeWardPrioritizationIndexEnum.value:
             if graph_type == DataTableConfigEnum.DataTable.value:
                return get_grantees_by_ward_prioritization_index_table_data(towns=towns)