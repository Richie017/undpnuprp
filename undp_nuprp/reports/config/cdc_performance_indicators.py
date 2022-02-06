"""
    Created by tareq on 3/22/17
"""
from undp_nuprp.reports.utils.enums.graph_types import DataTableConfigEnum
from undp_nuprp.reports.utils.enums.household_survey_indicator import HouseholdSurveyIndicatorEnum

__author__ = 'Tareq, Kaikobud'

cdc_performance_indicators = [
    {
        'name': 'CDC Performance, by city',
        'full_name': 'CDC Performance, by city',
        'indicator': HouseholdSurveyIndicatorEnum.DemoIndicator.value,
        'graph_types': [
            {
                'type': DataTableConfigEnum.DataTable.value + '1',
                'title': 'CDC Performance, by city'
            }
        ]
    },
]
