from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.managers.crmif_indicator.beneficiary_by_intervention_indicator import \
    get_beneficiary_by_intervention_table_data, \
    get_beneficiary_by_intervention_stacked_column_chart
from undp_nuprp.reports.managers.crmif_indicator.community_contract_indicator import get_community_contract_flat_data, \
    get_community_contract_table_data
from undp_nuprp.reports.managers.crmif_indicator.employed_people_by_intervention_indicator import \
    get_employed_people_by_intervention_table_data, get_employed_people_by_intervention_column_chart
from undp_nuprp.reports.managers.crmif_indicator.expenditure_by_intervention_indicator import \
    get_expenditure_by_intervention_flat_data, get_expenditure_by_intervention_table_data
from undp_nuprp.reports.managers.crmif_indicator.gender_by_intervention_indicator import \
    get_gender_by_intervention_stacked_bar_chart, get_gender_by_intervention_table_data
from undp_nuprp.reports.managers.crmif_indicator.intervention_type_indicator import get_intervention_type_pie_chart, \
    get_intervention_type_table_data
from undp_nuprp.reports.managers.crmif_indicator.interventions_less_then_half import \
    get_interventions_completed_less_than_half
from undp_nuprp.reports.managers.crmif_indicator.interventions_more_then_half import \
    get_interventions_completed_more_than_half
from undp_nuprp.reports.managers.crmif_indicator.on_budget_completed_intervention_indicator import \
    get_on_budget_completed_intervention_table_data, get_on_budget_completed_intervention_column_chart
from undp_nuprp.reports.managers.crmif_indicator.on_time_completed_intervention_indicator import \
    get_on_time_completed_intervention_table_data, get_on_time_completed_intervention_column_chart
from undp_nuprp.reports.managers.crmif_indicator.total_person_days_by_intervention_indicator import \
    get_total_person_days_by_intervention_table_data, get_total_person_days_by_intervention_column_chart
from undp_nuprp.reports.models.base.base import Report
from undp_nuprp.reports.utils.enums.crmif_indicator import CRMIFIndicatorEnum
from undp_nuprp.reports.utils.enums.graph_types import GraphTypeEnum, DataTableConfigEnum

__author__ = 'Shuvro'


@decorate(is_object_context,
          route(route='crmif-report', group='Infrastructure & Urban Services ', group_order=5,
                module=ModuleEnum.Reports, display_name="CRMIF", item_order=1))
class CRMIFReport(Report):
    class Meta:
        proxy = True
        app_label = 'reports'

    def build_report(self, wards=list(), from_time=None, to_time=None, indicator=None, graph_type=None):
        if indicator == CRMIFIndicatorEnum.CommunityContractIndicator.value:
            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_community_contract_flat_data(wards=wards, from_time=from_time, to_time=to_time)

            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_community_contract_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == CRMIFIndicatorEnum.InterventionTypeIndicator.value:
            if graph_type == GraphTypeEnum.PieChart.value:
                return get_intervention_type_pie_chart(wards=wards, from_time=from_time, to_time=to_time)

            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_intervention_type_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == CRMIFIndicatorEnum.ExpenditureIndicator.value:
            if graph_type == GraphTypeEnum.FlatHtml.value:
                return get_expenditure_by_intervention_flat_data(wards=wards, from_time=from_time, to_time=to_time)

            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_expenditure_by_intervention_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == CRMIFIndicatorEnum.GenderByIntervention.value:
            if graph_type == GraphTypeEnum.StackedColumnChart.value:
                return get_gender_by_intervention_stacked_bar_chart(wards=wards, from_time=from_time, to_time=to_time)

            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_gender_by_intervention_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == CRMIFIndicatorEnum.BeneficiaryByIntervention.value:
            if graph_type == GraphTypeEnum.StackedColumnChart.value:
                return get_beneficiary_by_intervention_stacked_column_chart(wards=wards, from_time=from_time,
                                                                            to_time=to_time)

            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_beneficiary_by_intervention_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == CRMIFIndicatorEnum.OnTimeCompletedIntervention.value:
            if graph_type == GraphTypeEnum.ColumnChart.value:
                return get_on_time_completed_intervention_column_chart(wards=wards, from_time=from_time,
                                                                       to_time=to_time)

            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_on_time_completed_intervention_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == CRMIFIndicatorEnum.OnBudgetCompletedIntervention.value:
            if graph_type == GraphTypeEnum.ColumnChart.value:
                return get_on_budget_completed_intervention_column_chart(wards=wards, from_time=from_time,
                                                                         to_time=to_time)

            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_on_budget_completed_intervention_table_data(wards=wards, from_time=from_time,
                                                                       to_time=to_time)

        if indicator == CRMIFIndicatorEnum.EmployedPeopleByIntervention.value:
            if graph_type == GraphTypeEnum.ColumnChart.value:
                return get_employed_people_by_intervention_column_chart(wards=wards, from_time=from_time,
                                                                        to_time=to_time)

            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_employed_people_by_intervention_table_data(wards=wards, from_time=from_time, to_time=to_time)

        if indicator == CRMIFIndicatorEnum.TotalPeopleByIntervention.value:
            if graph_type == GraphTypeEnum.ColumnChart.value:
                return get_total_person_days_by_intervention_column_chart(wards=wards, from_time=from_time,
                                                                          to_time=to_time)

            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_total_person_days_by_intervention_table_data(wards=wards, from_time=from_time,
                                                                        to_time=to_time)

        # if indicator == CRMIFIndicatorEnum.InterventionsLessThanHalf.value:
        #     if graph_type == DataTableConfigEnum.DataTable.value:
        #         return get_interventions_completed_less_than_half(wards=wards, from_time=from_time, to_time=to_time)
        #
        # if indicator == CRMIFIndicatorEnum.InterventionsMoreThanHalf.value:
        #     if graph_type == DataTableConfigEnum.DataTable.value:
        #         return get_interventions_completed_more_than_half(wards=wards, from_time=from_time, to_time=to_time)
