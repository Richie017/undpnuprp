"""
    Created by tareq on 3/22/17
"""
from django.utils.safestring import mark_safe

from undp_nuprp.reports.utils.enums.graph_types import GraphTypeEnum, DataTableConfigEnum
from undp_nuprp.reports.utils.enums.socio_economic_fund_indicator import SocioEconomicFundIndicatorEnum

__author__ = 'Tareq', 'Shuvro'

socio_economic_fund_grant_indicators = [
    {
        'name': 'Number of grantees, by type of grant',
        'full_name': 'Number of grantees, by type of grant',
        'indicator': SocioEconomicFundIndicatorEnum.GranteeEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.ColumnChart.value,
                'title': 'Number of grantees, by type of grant (all cities)',
                'y_axis_title': 'Number of grantee',
                'x_axis_title': 'Type of grant',
                'point_format': '{series.name}: {point.y:.0f}'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Number of grantees, by type of grant (by city)</b>')
            }
        ]
    },
    {
        'name': 'Age of grantees, by type of grant',
        'full_name': 'Age of grantees, by type of grant',
        'indicator': SocioEconomicFundIndicatorEnum.AgeIndicatorEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.PieChart.value,
                'title': 'Age distribution of grantees (all cities)',
                'point_format': '{point.y:.0f} <b>({point.percentage:.0f}%)</b>',
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Age distribution of grantees, by type of grant (by city)</b>')
            }
        ]
    },
    {
        'name': 'Gender of grantees by type of grant',
        'full_name': 'Gender of grantees by type of grant',
        'indicator': SocioEconomicFundIndicatorEnum.GenderEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.PieChart.value,
                'title': 'Gender of grantees (all cities)',
                'point_format': '{point.y:.0f} <b>({point.percentage:.0f}%)</b>',
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Gender of grantees, by type of grant (by city)</b>')
            }
        ]
    },
    {
        'name': 'Disability status of grantees, by type of grant',
        'full_name': 'Disability status of grantees, by type of grant',
        'indicator': SocioEconomicFundIndicatorEnum.DisabledIndicatorEnum.value,
        'graph_types': [
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Disability status of grantees, by type of grant (by city)</b>')
            },
            {
                'type': GraphTypeEnum.StackedBarChart.value,
                'title': 'Disability status of grantees (all cities)',
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
                'title': '% of grantee with a disability (all cities)',
                'point_format': '{point.y:.0f} <b>({point.percentage:.0f}%)</b>',
            }
        ]
    },
    {
        'name': 'Number of Apprenticeship grantees, by type of trade',
        'full_name': 'Number of Apprenticeship grantees, by type of trade',
        'indicator': SocioEconomicFundIndicatorEnum.ApBusinessAreaEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.PieChart.value,
                'title': 'Number of Apprenticeship grantees, by type of trade  (all cities)',
                'point_format': '{point.y:.0f} <b>({point.percentage:.0f}%)</b>',
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Number of Apprenticeship grantees, by type of trade (by city)</b>')
            }
        ]
    },
    {
        'name': 'Number of Business grantees, by type of business',
        'full_name': 'Number of Business grantees, by type of business',
        'indicator': SocioEconomicFundIndicatorEnum.BGBusinessAreaEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.PieChart.value,
                'title': 'Number of Business grantees, by type of business (all cities)',
                'point_format': '{point.y:.0f} <b>({point.percentage:.0f}%)</b>',
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Number of Business grantees, by type of business (by city)</b>')
            }
        ]
    },
    # {
    #     'name': 'Percentage of education grantees completing the academic year',
    #     'full_name': 'Percentage of education grantees completing the academic year',
    #     'indicator': SocioEconomicFundIndicatorEnum.EducationIndicatorEnum.value,
    #     'graph_types': [
    #         {
    #             'type': DataTableConfigEnum.DataTable.value,
    #             'title': 'Percentage of education grantees completing the academic year'
    #         }
    #     ]
    # },
    # {
    #     'name': 'MPI by grantee',
    #     'full_name': 'MPI by grantee',
    #     'indicator': SocioEconomicFundIndicatorEnum.GranteeMPIIndicatorEnum.value,
    #     'graph_types': [
    #         {
    #             'type': DataTableConfigEnum.DataTable.value,
    #             'title': 'MPI by grantee'
    #         }
    #     ]
    # },
    {
        'name': 'Total value of grants distributed, by type of grant',
        'full_name': 'Total value of grants distributed, by type of grant',
        'indicator': SocioEconomicFundIndicatorEnum.ValueOfGranteeIndicatorEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Total value of grants distributed'
            },
            {
                'type': GraphTypeEnum.ColumnChart.value,
                'title': 'Total value of grants distributed, by type of grant (all cities)',
                'y_axis_title': 'Total value of grants distributed',
                'x_axis_title': 'Type of grant',
                'point_format': '{series.name}: {point.y:.0f}'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Total value of grants distributed, by type of grant (by city)</b>')
            }
        ]
    },

      {
        'name': 'Number of Grantees by Ward Prioritization Index',
        'full_name': 'Number of Grantees by Ward Prioritization Index',
        'indicator': SocioEconomicFundIndicatorEnum.GranteeWardPrioritizationIndexEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.ColumnChart.value,
                'title': 'Total value of grants distributed, by Ward Prioritization Index (all cities)',
                'y_axis_title': 'Total value of grants distributed',
                'x_axis_title': 'Type of grant',
                'point_format': '{series.name}: {point.y:.0f}'
            },{
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Number of Grantees by Ward Prioritization Index</b>')
            }
        ]
    }
]
