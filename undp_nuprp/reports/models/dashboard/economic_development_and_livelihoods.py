from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.managers.economic_development_and_livelihoods.economic_development_and_livelihood import \
    get_established_scc_indicator_table_data, get_bi_annual_meeting_indicator_table_data, \
    get_initiatives_taken_by_scc_indicator_table_data
from undp_nuprp.reports.models import Report
from undp_nuprp.reports.utils.enums.economic_development_and_planning_indicator import \
    EconomicDevelopmentAndLivelihoodEnum
from undp_nuprp.reports.utils.enums.graph_types import DataTableConfigEnum


@decorate(is_object_context,
          route(route='economic-development-and-livelihood-report',
                group='Local Economy Livelihood and Financial Inclusion ',
                group_order=3, module=ModuleEnum.Reports, display_name="Gender",
                item_order=5))
class EconomicDevelopmentAndLivelihood(Report):
    class Meta:
        proxy = True
        app_label = 'reports'

    def build_report(self, from_time=None, to_time=None, indicator=None, graph_type=None):
        if indicator == EconomicDevelopmentAndLivelihoodEnum.EstablishedSCC.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_established_scc_indicator_table_data(from_time, to_time)
        elif indicator == EconomicDevelopmentAndLivelihoodEnum.BiAnnualMeeting.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_bi_annual_meeting_indicator_table_data(from_time, to_time)
        elif indicator == EconomicDevelopmentAndLivelihoodEnum.InitiativesBySCC.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_initiatives_taken_by_scc_indicator_table_data(from_time, to_time)
