from django.utils.safestring import mark_safe

from undp_nuprp.reports.utils.enums.crmif_indicator import CRMIFIndicatorEnum
from undp_nuprp.reports.utils.enums.graph_types import GraphTypeEnum, DataTableConfigEnum

__author__ = 'Shuvro'

crmif_indicator = [
    {
        'name': 'Number of contracts',
        'full_name': 'Number of contracts',
        'indicator': CRMIFIndicatorEnum.CommunityContractIndicator.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Number of contracts (all cities)'

            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Number of contracts (by city)</b>')
            }
        ]
    },
    {
        'name': 'Number of interventions, by type',
        'full_name': 'Number of interventions, by type',
        'indicator': CRMIFIndicatorEnum.InterventionTypeIndicator.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.PieChart.value,
                'title': 'Number of interventions, by type (all cities)',
                'point_format': '{point.y:.0f} <b>({point.percentage:.0f}%)</b>'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Number of interventions, by type (by city)</b>')
            }
        ]
    },
    {
        'name': 'Expenditure to date (BDT)',
        'full_name': 'Expenditure to date (BDT)',
        'indicator': CRMIFIndicatorEnum.ExpenditureIndicator.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Expenditure to date (all cities)'

            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Expenditure to date (by city)</b>')
            }
        ]
    },
    {
        'name': 'Gender of beneficiaries, by type of intervention',
        'full_name': 'Gender of beneficiaries, by type of intervention',
        'indicator': CRMIFIndicatorEnum.GenderByIntervention.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.StackedColumnChart.value,
                'title': 'Gender of beneficiaries, by type of intervention (all cities)',
                'y_axis_title': '%',
                'x_axis_title': 'Type of intervention',
                'point_format': '{series.name}: {point.y:.0f}%',
                'config': {
                    'yAxis': {
                        'max': 100, 'min': 0
                    }
                }
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Gender of beneficiaries, by type of intervention (by city)</b>')
            }
        ]
    },
    {
        'name': 'Type of beneficiaries (PG/ Non-PG), by type of intervention',
        'full_name': 'Type of beneficiaries (PG/ Non-PG), by type of intervention',
        'indicator': CRMIFIndicatorEnum.BeneficiaryByIntervention.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.StackedColumnChart.value,
                'title': 'Type of beneficiary (PG/ Non-PG), by type of intervention (all cities)',
                'point_format': '{series.name}: {point.y:.0f}%',
                'x_axis_title': 'Type of intervention',
                'y_axis_title': '%',
                'config': {
                    'yAxis': {
                        'max': 100, 'min': 0
                    }
                }
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Type of beneficiary (PG/ Non-PG), by type of intervention (by city)</b>')
            }
        ]
    },

    {
        'name': '% of interventions completed on time',
        'full_name': '% of interventions completed on time',
        'indicator': CRMIFIndicatorEnum.OnTimeCompletedIntervention.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.ColumnChart.value,
                'title': '% of interventions completed on time, by type (all cities)',
                'y_axis_title': '% of interventions completed on time',
                'x_axis_title': 'Type of intervention',
                'point_format': '{series.name}: {point.y:.0f}%'

            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>% of interventions completed on time, by type (by city)</b>')
            }
        ]
    },
    {
        'name': '% of interventions completed within budget',
        'full_name': '% of interventions completed within budget',
        'indicator': CRMIFIndicatorEnum.OnBudgetCompletedIntervention.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.ColumnChart.value,
                'title': '% of interventions completed within budget, by type (all cities)',
                'y_axis_title': '% of interventions completed within budget',
                'x_axis_title': 'Type of intervention',
                'point_format': '{series.name}: {point.y:.0f}%'

            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>% of interventions completed within budget, by type (by city)</b>')
            }
        ]
    },

    {
        'name': 'Total number of people employed, by type of intervention',
        'full_name': 'Total number of people employed, by type of intervention',
        'indicator': CRMIFIndicatorEnum.EmployedPeopleByIntervention.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.ColumnChart.value,
                'title': 'Total number of people employed, by type of intervention (all cities)',
                'y_axis_title': 'Total number of people employed',
                'x_axis_title': 'Type of intervention',
                'point_format': '{series.name}: {point.y:.0f}'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Total number of people employed, by type of intervention (by city)</b>')
            }
        ]
    },

    {
        'name': 'Total number of person days, by type of intervention',
        'full_name': 'Total number of person days, by type of intervention',
        'indicator': CRMIFIndicatorEnum.TotalPeopleByIntervention.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.ColumnChart.value,
                'title': 'Total number of person days, by type of intervention (all cities)',
                'y_axis_title': 'Total number of person days',
                'x_axis_title': 'Type of intervention',
                'point_format': '{series.name}: {point.y:.0f}'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Total number of person days, by type of intervention (by city)</b>')
            }
        ]
    },

# {
#         'name': 'Number of interventions completed less than 50%',
#         'full_name': 'Number of interventions completed less than 50%',
#         'indicator': CRMIFIndicatorEnum.InterventionsLessThanHalf.value,
#         'graph_types': [
#             {
#                 'type': DataTableConfigEnum.DataTable.value,
#                 'title': mark_safe('<b>Number of interventions completed less than 50% (by city)</b>')
#             }
#         ]
#     },
#
#     {
#         'name': 'Number of interventions completed more than 50%',
#         'full_name': 'Number of interventions completed more than 50%',
#         'indicator': CRMIFIndicatorEnum.InterventionsMoreThanHalf.value,
#         'graph_types': [
#             {
#                 'type': DataTableConfigEnum.DataTable.value,
#                 'title': mark_safe('<b>Number of interventions completed more than 50% (by city)</b>')
#             }
#         ]
#     }

]
