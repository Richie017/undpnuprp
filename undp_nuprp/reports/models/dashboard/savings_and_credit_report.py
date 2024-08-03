from datetime import datetime

from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.managers.savings_and_credit.savings_and_credit_cumulative_savings_indicator import \
    get_scg_member_cumulative_savings_indicator_flat_data, \
    get_scg_member_cumulative_savings_indicator_column_chart_data, \
    get_scg_member_cumulative_savings_indicator_table_data
from undp_nuprp.reports.managers.savings_and_credit.savings_and_credit_fund_value_indicator import \
    get_scg_member_fund_value_flat_data, get_scg_member_fund_value_column_chart_data, \
    get_scg_member_fund_value_table_data
from undp_nuprp.reports.managers.savings_and_credit.savings_and_credit_loan_disbursement import \
    get_scg_member_loan_disbursement_flat_data, get_scg_member_loan_disbursement_column_chart_data, \
    get_scg_member_loan_disbursement_table_data
from undp_nuprp.reports.managers.savings_and_credit.savings_and_credit_loan_outstanding_indicator import \
    get_scg_member_loan_outstanding_flat_data, get_scg_member_loan_outstanding_column_chart_data, \
    get_scg_member_loan_outstanding_table_data
from undp_nuprp.reports.managers.savings_and_credit.savings_and_credit_member_percent_indicator import \
    get_scg_member_percent_indicator_flat_data, get_scg_member_percent_indicator_column_chart_data, \
    get_scg_member_percent_indicator_table_data
from undp_nuprp.reports.managers.savings_and_credit.savings_and_credit_members_indicator import \
    get_scg_member_number_indicator_flat_data, get_scg_member_number_indicator_table_data, \
    get_scg_member_number_indicator_column_chart_data
from undp_nuprp.reports.managers.savings_and_credit.savings_and_credit_money_in_bank_indicator import \
    get_scg_member_money_in_bank_indicator_flat_data, get_scg_member_money_in_bank_indicator_column_chart_data, \
    get_scg_member_money_in_bank_indicator_table_data
from undp_nuprp.reports.managers.savings_and_credit.savings_and_credit_on_time_realization_indicator import \
    get_scg_member_on_time_realization_column_chart_data, get_scg_member_on_time_realization_table_data, \
    get_scg_member_on_time_realization_flat_data
from undp_nuprp.reports.managers.savings_and_credit.savings_and_credit_savings_indicator import \
    get_scg_member_saving_and_credit_savings_indicator_flat_data, \
    get_scg_member_saving_and_credit_savings_indicator_chart_data, \
    get_scg_member_saving_and_credit_savings_indicator_table_data
from undp_nuprp.reports.models.base.base import Report
from undp_nuprp.reports.utils.enums.graph_types import GraphTypeEnum, DataTableConfigEnum
from undp_nuprp.reports.utils.enums.savings_and_credit_indicator import SavingsAndCreditIndicatorEnum

__author__ = 'Ashraful', 'Shuvro'


@decorate(is_object_context,
          route(route='savings-and-credit', group='Social Mobilization and Community Capacity Building ',
                group_order=2, module=ModuleEnum.Reports,
                display_name="Savings and Credit", item_order=1))
class SavingsAndCreditReport(Report):
    class Meta:
        proxy = True
        app_label = 'reports'

    def build_report(self, wards=list(), from_time=None, to_time=None, indicator=None, graph_type=None):
        if indicator == SavingsAndCreditIndicatorEnum.SCGMemberEnum.value:
            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_scg_member_number_indicator_flat_data(wards=wards, from_time=from_time,
                                                                 to_time=to_time)
            if graph_type == GraphTypeEnum.ColumnChart.value:
                return get_scg_member_number_indicator_column_chart_data(wards=wards, from_time=from_time,
                                                                         to_time=to_time)
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_scg_member_number_indicator_table_data(wards=wards, from_time=from_time,
                                                                  to_time=to_time)

        if indicator == SavingsAndCreditIndicatorEnum.SCGPercentEnum.value:
            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_scg_member_percent_indicator_flat_data(wards=wards, from_time=from_time,
                                                                  to_time=to_time)
            if graph_type == GraphTypeEnum.ColumnChart.value:
                return get_scg_member_percent_indicator_column_chart_data(wards=wards, from_time=from_time,
                                                                          to_time=to_time)
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_scg_member_percent_indicator_table_data(wards=wards, from_time=from_time,
                                                                          to_time=to_time)

        if indicator == SavingsAndCreditIndicatorEnum.SCGSavingEnum.value:
            _today = datetime.now()
            _reporting_month = _today.month - 1 if _today.month > 1 else 12
            _reporting_year = _today.year if _today.month > 1 else _today.year - 1
            _reporting_date = datetime.now().replace(year=_reporting_year, month=_reporting_month, day=1, hour=0,
                                                     minute=0, second=0, microsecond=0)

            from_time = from_time if from_time else int(_reporting_date.timestamp() * 1000)

            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_scg_member_saving_and_credit_savings_indicator_flat_data(wards=wards, from_time=from_time,
                                                                                    to_time=to_time)
            if graph_type == GraphTypeEnum.ColumnChart.value:
                return get_scg_member_saving_and_credit_savings_indicator_chart_data(wards=wards, from_time=from_time,
                                                                                     to_time=to_time)

            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_scg_member_saving_and_credit_savings_indicator_table_data(wards=wards, from_time=from_time,
                                                                                     to_time=to_time)

        if indicator == SavingsAndCreditIndicatorEnum.CumulativeSavingEnum.value:
            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_scg_member_cumulative_savings_indicator_flat_data()
            if graph_type == GraphTypeEnum.ColumnChart.value:
                return get_scg_member_cumulative_savings_indicator_column_chart_data(wards=wards, from_time=from_time,
                                                                                     to_time=to_time)
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_scg_member_cumulative_savings_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == SavingsAndCreditIndicatorEnum.SCGLoanEnum.value:
            _today = datetime.now()
            _reporting_month = _today.month - 1 if _today.month > 1 else 12
            _reporting_year = _today.year if _today.month > 1 else _today.year - 1
            _reporting_date = datetime.now().replace(year=_reporting_year, month=_reporting_month, day=1, hour=0,
                                                     minute=0, second=0, microsecond=0)

            from_time = from_time if from_time else int(_reporting_date.timestamp() * 1000)

            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_scg_member_loan_disbursement_flat_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == GraphTypeEnum.ColumnChart.value:
                return get_scg_member_loan_disbursement_column_chart_data(wards=wards, from_time=from_time,
                                                                          to_time=to_time)
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_scg_member_loan_disbursement_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == SavingsAndCreditIndicatorEnum.CumulativeLoanEnum.value:
            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_scg_member_loan_disbursement_flat_data(wards=wards, from_time=from_time, to_time=to_time)

            if graph_type == GraphTypeEnum.ColumnChart.value:
                return get_scg_member_loan_disbursement_column_chart_data(wards=wards, from_time=from_time,
                                                                          to_time=to_time)
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_scg_member_loan_disbursement_table_data(wards=wards,from_time=from_time, to_time=to_time)

        if indicator == SavingsAndCreditIndicatorEnum.CumulativeOutStandingLoanEnum.value:
            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_scg_member_loan_outstanding_flat_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == GraphTypeEnum.ColumnChart.value:
                return get_scg_member_loan_outstanding_column_chart_data(wards=wards, from_time=from_time,
                                                                         to_time=to_time)
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_scg_member_loan_outstanding_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == SavingsAndCreditIndicatorEnum.SCGMoneyEnum.value:
            _today = datetime.now()
            _reporting_month = _today.month - 1 if _today.month > 1 else 12
            _reporting_year = _today.year if _today.month > 1 else _today.year - 1
            _reporting_date = datetime.now().replace(year=_reporting_year, month=_reporting_month, day=1, hour=0,
                                                     minute=0, second=0, microsecond=0)

            from_time = from_time if from_time else int(_reporting_date.timestamp() * 1000)

            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_scg_member_money_in_bank_indicator_flat_data(wards=wards, from_time=from_time,
                                                                        to_time=to_time)
            if graph_type == GraphTypeEnum.ColumnChart.value:
                return get_scg_member_money_in_bank_indicator_column_chart_data(wards=wards, from_time=from_time,
                                                                                to_time=to_time)
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_scg_member_money_in_bank_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == SavingsAndCreditIndicatorEnum.SCGFundEnum.value:
            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_scg_member_fund_value_flat_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == GraphTypeEnum.ColumnChart.value:
                return get_scg_member_fund_value_column_chart_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_scg_member_fund_value_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == SavingsAndCreditIndicatorEnum.SCGOntimeEnum.value:
            _today = datetime.now()
            _reporting_month = _today.month - 1 if _today.month > 1 else 12
            _reporting_year = _today.year if _today.month > 1 else _today.year - 1
            _reporting_date = datetime.now().replace(year=_reporting_year, month=_reporting_month, day=1, hour=0,
                                                     minute=0, second=0, microsecond=0)

            from_time = from_time if from_time else int(_reporting_date.timestamp() * 1000)

            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_scg_member_on_time_realization_flat_data(wards=wards, from_time=from_time, to_time=to_time)
            if graph_type == GraphTypeEnum.ColumnChart.value:
                return get_scg_member_on_time_realization_column_chart_data(wards=wards, from_time=from_time,
                                                                             to_time=to_time)
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_scg_member_on_time_realization_table_data(wards=wards, from_time=from_time, to_time=to_time)

