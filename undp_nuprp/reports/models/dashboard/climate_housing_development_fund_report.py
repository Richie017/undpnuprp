from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.managers.housing_finance.climate_housing_development_fund import \
    get_chdf_status_indicator_table_data, get_implementation_status_indicator_table_data
from undp_nuprp.reports.managers.not_done_manager import get_blank_report_data
from undp_nuprp.reports.models.base.base import Report
from undp_nuprp.reports.utils.enums.graph_types import DataTableConfigEnum
from undp_nuprp.reports.utils.enums.climate_housing_development_fund_indicator import \
    ClimateHousingDevelopmentFundIndicatorEnum

__author__ = 'Ashraful'


@decorate(is_object_context,
          route(route='climate-housing-development-fund', group='Housing Finance ', group_order=4,
                module=ModuleEnum.Reports,
                display_name="Climate Housing Development Fund", item_order=1))
class ClimateHousingDevelopmentFundReport(Report):
    class Meta:
        proxy = True
        app_label = 'reports'

    def build_report(self, cities=list, indicator=None, graph_type=None):
        if indicator == ClimateHousingDevelopmentFundIndicatorEnum.CHDFStatusIndicator.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_chdf_status_indicator_table_data(cities)
        if indicator == ClimateHousingDevelopmentFundIndicatorEnum.ImplementationStatusIndicator.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_implementation_status_indicator_table_data(cities)
        return get_blank_report_data()
