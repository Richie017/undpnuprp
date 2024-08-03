from django.utils.safestring import mark_safe

from undp_nuprp.reports.utils.enums.graph_types import GraphTypeEnum, DataTableConfigEnum
from undp_nuprp.reports.utils.enums.pg_hh_head_indicator import PGHHHeadIndicatorEnum

__author__ = "Shama"

pg_hh_head_information_indicators = [
    {
        'name': 'Gender of HH head',
        'full_name': 'Gender of HH head',
        'indicator': PGHHHeadIndicatorEnum.HHHeadGenderEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.PieChart.value,
                'title': 'Gender of HH head (all cities)',
                'point_format': '{point.y:.0f} <b>({point.percentage:.0f}%)</b>',
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Gender of HH head, by city</b>')
            }
        ]
    },
    {
        'name': 'Employment status of HH head',
        'full_name': 'Employment status of HH head',
        'indicator': PGHHHeadIndicatorEnum.HHHeadEmploymentEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.PieChart.value,
                'title': 'Employment status of HH head (all cities)',
                'point_format': '{point.y:.0f} <b>({point.percentage:.0f}%)</b>',
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Employment status of HH head, by city</b>')
            }
        ]
    },
    {
        'name': 'Education attainment of HH head',
        'full_name': 'Education attainment of HH head',
        'indicator': PGHHHeadIndicatorEnum.HHHeadEducationEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.PieChart.value,
                'title': 'Education attainment status of HH head (all cities)',
                'point_format': '{point.y:.0f} <b>({point.percentage:.0f}%)</b>',
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Education attainment of HH head, by city</b>')
            }
        ]
    },
    {
        'name': 'Disability status of HH Head',
        'full_name': 'Disability status of HH Head',
        'indicator': PGHHHeadIndicatorEnum.HHHeadDisabilityEnum.value,
        'graph_types': [
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Disability status of HH head, by city</b>')
            },
            {
                'type': GraphTypeEnum.StackedBarChart.value,
                'title': 'Disability status of HH head (all cities)',
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
                'title': '% of HH head with a disability (all cities)',
                'point_format': '{point.y:.0f} <b>({point.percentage:.0f}%)</b>',
            }
        ]
    }
]
