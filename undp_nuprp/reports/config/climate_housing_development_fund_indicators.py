from undp_nuprp.reports.utils.enums.climate_housing_development_fund_indicator import \
    ClimateHousingDevelopmentFundIndicatorEnum
from undp_nuprp.reports.utils.enums.graph_types import GraphTypeEnum, DataTableConfigEnum
from undp_nuprp.reports.utils.enums.household_survey_indicator import HouseholdSurveyIndicatorEnum

__author__ = 'Ashraful'

climate_housing_development_fund_indicator = [
    {
        'name': 'Number of PG and non PG households receiving a loan',
        'full_name': 'Value of savings generated from savings and credit groups',
        'indicator': HouseholdSurveyIndicatorEnum.DemoIndicator.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': '% of PG members involved in Savings and Credit project'
            }
        ]
    },
    {
        'name': 'Average value of CHDF loan',
        'full_name': 'Value of savings generated from savings and credit groups',
        'indicator': HouseholdSurveyIndicatorEnum.DemoIndicator.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': '% of PG members involved in Savings and Credit project'
            }
        ]
    },
    {
        'name': 'Status of CHDF city-wise',
        'full_name': 'Value of savings generated from savings and credit groups',
        'indicator': ClimateHousingDevelopmentFundIndicatorEnum.CHDFStatusIndicator.value,
        'graph_types': [
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': 'Staus of CHDF city-wise (Reporting Month)'
            }
        ]
    },
    {
        'name': 'Implementation Status',
        'full_name': 'Value of savings generated from savings and credit groups',
        'indicator': ClimateHousingDevelopmentFundIndicatorEnum.ImplementationStatusIndicator.value,
        'graph_types': [
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': 'Implementation Status (Reporting month)'
            }
        ]
    }
]
