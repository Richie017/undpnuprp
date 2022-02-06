from django.utils.safestring import mark_safe

from undp_nuprp.reports.utils.enums.graph_types import GraphTypeEnum, DataTableConfigEnum
from undp_nuprp.reports.utils.enums.pg_member_indicator import PGMemberIndicatorEnum

__author__ = "Shama"

pg_member_information_indicators = [
    {
        'name': 'Number of PG members',
        'full_name': 'Number of PG members',
        'indicator': PGMemberIndicatorEnum.PGNumberEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': mark_safe('<b>Number of PG members (all cities)</b>')
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Number of PG members, by city</b>')
            },
        ]
    },
    {
        'name': 'Age of PG members',
        'full_name': 'Age of PG members',
        'indicator': PGMemberIndicatorEnum.PGAgeEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.PieChart.value,
                'title': 'Age distribution of PG members (all cities)',
                'point_format': '{point.y:.0f} <b>({point.percentage:.0f}%)</b>',
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Age distribution of PG members, by city</b>')
            }
        ]
    },
    {
        'name': 'Religion of PG members',
        'full_name': 'Religion of PG members',
        'indicator': PGMemberIndicatorEnum.PGReligionEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.PieChart.value,
                'title': 'Religion of PG members (all cities)',
                'point_format': '{point.y:.0f} <b>({point.percentage:.0f}%)</b>',
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Religion of PG members, by city</b>')
            }
        ]
    },
    {
        'name': 'Ethnicity of PG members',
        'full_name': 'Ethnicity of PG members',
        'indicator': PGMemberIndicatorEnum.PGEthnicityEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.PieChart.value,
                'title': 'Ethnicity of PG members (all cities)',
                'point_format': '{point.y:.0f} <b>({point.percentage:.0f}%)</b>',
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Ethnicity of PG members, by city</b>')
            }
        ]
    },
    {
        'name': 'Marital status of PG members',
        'full_name': 'Marital status of PG members',
        'indicator': PGMemberIndicatorEnum.PGMaritalStatusEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.PieChart.value,
                'title': 'Marital status of PG members (all cities)',
                'point_format': '{point.y:.0f} <b>({point.percentage:.0f}%)</b>',
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Marital status of PG members, by city</b>')
            }
        ]
    },
    {
        'name': 'Disability status of PG members',
        'full_name': 'Disability status of PG members',
        'indicator': PGMemberIndicatorEnum.PGDisabilityEnum.value,
        'graph_types': [
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Disability status of PG members, by city</b>')
            },
            {
                'type': GraphTypeEnum.StackedBarChart.value,
                'title': 'Disability status of PG members (all cities)',
                'y_axis_title': '% of disability',
                'x_axis_title': 'Type of disability',
                'point_format': '{series.name}: {point.y:.0f}%',
                'config': {
                    'yAxis': {
                        'max': 100, 'min': 0
                    }
                }
            },
            {
                'type': GraphTypeEnum.PieChart.value,
                'title': '% of PG members with a disability (all cities)',
                'point_format': '{point.y:.0f} <b>({point.percentage:.0f}%)</b>',
            }
        ]
    },
    {
        'name': '% of PG members who are HH head',
        'full_name': '% of PG members who are HH head',
        'indicator': PGMemberIndicatorEnum.PGHHEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': '% of PG members who are HH head (all cities)'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>% of PG members who are HH head, by city</b>')
            }
        ]
    },
    {
        'name': 'Gender of PG members',
        'full_name': 'Gender of PG members',
        'indicator': PGMemberIndicatorEnum.PGGenderEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.PieChart.value,
                'title': 'Gender of PG members (all cities)',
                'point_format': '{point.y:.0f} <b>({point.percentage:.0f}%)</b>',
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Gender of PG members, by city</b>')
            },
        ]
    },
    {
        'name': 'Employment status of PG members',
        'full_name': 'Employment status of PG members',
        'indicator': PGMemberIndicatorEnum.PGEmploymentEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.PieChart.value,
                'title': 'Employment status of PG members (all cities)',
                'point_format': '{point.y:.0f} <b>({point.percentage:.0f}%)</b>',
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Employment status of PG members, by city</b>')
            }
        ]
    },
    {
        'name': 'Education attainment of PG members',
        'full_name': 'Education attainment of PG members',
        'indicator': PGMemberIndicatorEnum.PGEducationEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.PieChart.value,
                'title': 'Education attainment of PG members (all cities)',
                'point_format': '{point.y:.0f} <b>({point.percentage:.0f}%)</b>',
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Education attainment of PG members, by city</b>')
            }
        ]
    }
]
