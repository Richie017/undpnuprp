"""
    Created by tareq on 3/22/17
"""
from django.utils.safestring import mark_safe

from undp_nuprp.reports.utils.enums.community_mobilization_indicator import CommunityMobilizationIndicatorEnum
from undp_nuprp.reports.utils.enums.graph_types import GraphTypeEnum, DataTableConfigEnum
from undp_nuprp.reports.utils.enums.household_survey_indicator import HouseholdSurveyIndicatorEnum

__author__ = 'Tareq'

community_mobilization_indicators = [
    {
        'name': 'Number of Primary Group members registered',
        'full_name': 'Number of Primary Group members registered',
        'indicator': CommunityMobilizationIndicatorEnum.PGMemberEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Number of Primary Group members registered'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Number of Primary Group members registered, by city</b>')
            },
        ]
    },
    {
        'name': 'Number of Primary Groups in which members registered',
        'full_name': 'Number of Primary Groups in which members registered',
        'indicator': CommunityMobilizationIndicatorEnum.PGNumberEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Number of Primary Groups in which members registered'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Number of Primary Groups in which members registered, by city</b>')
            },
        ]
    },
    {
        'name': 'Number of CDCs in which members registered',
        'full_name': 'Number of CDCs in which members registered',
        'indicator': CommunityMobilizationIndicatorEnum.CDCNumberEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Number of CDC(s)'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title':  mark_safe('<b>Number of CDCs in which members registered, by city</b>')
            }
        ]
    },
    {
        'name': 'Number of CDC Clusters in which members registered',
        'full_name': 'Number of CDC Clusters in which members registered',
        'indicator': CommunityMobilizationIndicatorEnum.CDCClusterNumberEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Number of CDC Clusters in which members registered'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title':  mark_safe('<b>Number of CDC Clusters in which members registered, by city</b>')
            }
        ]
    },
    {
        'name': 'Number of Primary Group members mobilized (reactivated and newly formed)',
        'full_name': 'Number of Primary Group members mobilized (reactivated and newly formed)',
        'indicator': CommunityMobilizationIndicatorEnum.AllPGMemberEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Number of Primary Group members mobilized (reactivated and newly formed)'
            }
        ]
    },
    {
        'name': 'Number of Primary Groups mobilized (reactivated and newly formed)',
        'full_name': 'Number of Primary Groups mobilized (reactivated and newly formed)',
        'indicator': CommunityMobilizationIndicatorEnum.AllPGNumberEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Number of Primary Groups mobilized (reactivated and newly formed)'
            }
        ]
    },
    {
        'name': 'Number of CDCs mobilized (reactivated and newly formed)',
        'full_name': 'Number of CDCs mobilized (reactivated and newly formed)',
        'indicator': CommunityMobilizationIndicatorEnum.AllCDCNumberEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Number of CDCs mobilized (reactivated and newly formed)'
            }
        ]
    },
    {
        'name': 'Number of CDC clusters mobilized (reactivated and newly formed)',
        'full_name': 'Number of CDC clusters mobilized (reactivated and newly formed)',
        'indicator': CommunityMobilizationIndicatorEnum.AllCDCClusterNumberEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Number of CDC clusters mobilized (reactivated and newly formed)'
            }
        ]
    },
]
