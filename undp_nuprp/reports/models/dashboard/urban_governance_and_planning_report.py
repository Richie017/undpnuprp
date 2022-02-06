from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.managers.urban_governance_and_planning.urban_governance_and_planning_indicator import \
    get_ugp_ward_committee_indicator_table_data, get_ugp_standing_committee_indicator_table_data, \
    get_ugp_institutional_financial_capability_indicator_table_data
from undp_nuprp.reports.models import Report
from undp_nuprp.reports.utils.enums.graph_types import DataTableConfigEnum
from undp_nuprp.reports.utils.enums.urban_governance_and_planning_indicator import \
    UrbanGovernanceAndPlanningIndicatorEnum


@decorate(is_object_context,
          route(route='urban-governance-and-planning-report', group='Planning and Urban Governance ', group_order=1,
                module=ModuleEnum.Reports, display_name="Planning and Urban Governance", item_order=1))
class UrbanGovernanceAndPlanningReport(Report):
    class Meta:
        proxy = True
        app_label = 'reports'

    def build_report(self, from_time=None, to_time=None, indicator=None, graph_type=None):
        if indicator == UrbanGovernanceAndPlanningIndicatorEnum.WardCommittee.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_ugp_ward_committee_indicator_table_data(from_time, to_time)
        if indicator == UrbanGovernanceAndPlanningIndicatorEnum.InstitutionalFinancialCapability.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_ugp_institutional_financial_capability_indicator_table_data(from_time, to_time)
        if indicator == UrbanGovernanceAndPlanningIndicatorEnum.StandingCommittee.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_ugp_standing_committee_indicator_table_data(from_time, to_time)
