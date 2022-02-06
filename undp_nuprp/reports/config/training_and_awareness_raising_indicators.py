from undp_nuprp.reports.utils.enums.graph_types import GraphTypeEnum
from undp_nuprp.reports.utils.enums.household_survey_indicator import HouseholdSurveyIndicatorEnum

__author__ = 'Ashraful'

training_and_awareness_raising_indicator = [
    {
        'name': 'Number of CDC leaders received training related to VAWG and early marriage',
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
        'name': 'Percentage of CDC leaders, who have received training on VAWG and early marriage with improved awareness above baseline',
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
        'name': 'Percentage of PG members who have received counselling and/ or BCC messaging',
        'full_name': 'Value of savings generated from savings and credit groups',
        'indicator': HouseholdSurveyIndicatorEnum.DemoIndicator.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': '% of PG members involved in Savings and Credit project'
            }
        ]
    }
]
