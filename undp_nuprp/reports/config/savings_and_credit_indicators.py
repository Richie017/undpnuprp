from django.utils.safestring import mark_safe

from undp_nuprp.reports.utils.enums.graph_types import GraphTypeEnum, DataTableConfigEnum
from undp_nuprp.reports.utils.enums.savings_and_credit_indicator import SavingsAndCreditIndicatorEnum

__author__ = 'Ashraful'

savings_and_credit_indicator = [
    {
        'name': 'Number of savings & credit group members',
        'full_name': 'Number of savings & credit group members',
        'indicator': SavingsAndCreditIndicatorEnum.SCGMemberEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Number of savings & credit group members'
            },
            {
                'type': GraphTypeEnum.ColumnChart.value,
                'title': 'Number of savings & credit group members, by city',
                'y_axis_title': 'SCG Members',
                'x_axis_title': 'City/Town',
                'point_format': '{series.name}: {point.y:.0f}'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Number of savings & credit group members, by city</b>')
            }
        ]
    },
    {
        'name': ' % of PG members involved in Savings and Credit project',
        'full_name': ' % of PG members involved in Savings and Credit project',
        'indicator': SavingsAndCreditIndicatorEnum.SCGPercentEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': ' % of PG members involved in Savings and Credit project'
            },
            {
                'type': GraphTypeEnum.ColumnChart.value,
                'title': '% of SCG Members, by city',
                'y_axis_title': '% of SCG Members',
                'x_axis_title': 'City/Town',
                'point_format': '{series.name}: {point.y:.0f}'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>% of SCG Members, by city</b>')
            }
        ]
    },
    {
        'name': 'Value of savings balance for the reporting period',
        'full_name': 'Value of savings balance for the reporting period',
        'indicator': SavingsAndCreditIndicatorEnum.SCGSavingEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Value of savings balance for the reporting period'
            },
            {
                'type': GraphTypeEnum.ColumnChart.value,
                'title': 'Value of savings balance for the reporting period, by city',
                'y_axis_title': 'Savings balance',
                'x_axis_title': 'City/Town',
                'point_format': '{series.name}: {point.y:.0f}'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Value of savings balance for the reporting period, by city</b>')
            }
        ]
    },
    {
        'name': 'Cumulative value of total savings',
        'full_name': 'Cumulative value of total savings',
        'indicator': SavingsAndCreditIndicatorEnum.CumulativeSavingEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Cumulative value of total savings'
            },
            {
                'type': GraphTypeEnum.ColumnChart.value,
                'title': 'Cumulative value of total savings, by city',
                'y_axis_title': 'Cumulative savings balance',
                'x_axis_title': 'City/Town',
                'point_format': '{series.name}: {point.y:.0f}'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Cumulative value of total savings, by city</b>')
            }
        ]
    },
    {
        'name': 'Value of loans disbursed during the reporting period',
        'full_name': 'Value of loans disbursed during the reporting period',
        'indicator': SavingsAndCreditIndicatorEnum.SCGLoanEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Value of loans disbursed during the reporting period'
            },
            {
                'type': GraphTypeEnum.ColumnChart.value,
                'title': 'Value of loans disbursed during the reporting period, by city',
                'y_axis_title': 'value of disbursed Loans',
                'x_axis_title': 'City/Town',
                'point_format': '{series.name}: {point.y:.0f}'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Value of loans disbursed during the reporting period, by city</b>')
            }
        ]
    },
    {
        'name': 'Cumulative value of loans disbursed',
        'full_name': 'Cumulative value of loans disbursed',
        'indicator': SavingsAndCreditIndicatorEnum.CumulativeLoanEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Cumulative value of loans disbursed'
            },
            {
                'type': GraphTypeEnum.ColumnChart.value,
                'title': 'Cumulative value of savings (All SCG/CDCs), by city',
                'y_axis_title': 'Cumulative value of disbursed Loans',
                'x_axis_title': 'City/Town',
                'point_format': '{series.name}: {point.y:.0f}'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Cumulative value of savings (All SCG/CDCs), by city</b>')
            }
        ]
    },
    {
        'name': 'Cumulative value of outstanding loans',
        'full_name': 'Cumulative value of outstanding loans',
        'indicator': SavingsAndCreditIndicatorEnum.CumulativeOutStandingLoanEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Cumulative value of outstanding loans'
            },
            {
                'type': GraphTypeEnum.ColumnChart.value,
                'title': 'Cumulative value of outstanding loans, by city',
                'y_axis_title': 'Cumulative value of outstanding loans',
                'x_axis_title': 'City/Town',
                'point_format': '{series.name}: {point.y:.0f}'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Cumulative value of outstanding loans, by city</b>')
            }
        ]
    },
    {
        'name': 'Value of money in the bank during reporting month',
        'full_name': 'Value of money in the bank during reporting month',
        'indicator': SavingsAndCreditIndicatorEnum.SCGMoneyEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Value of money in the bank during reporting month'
            },
            {
                'type': GraphTypeEnum.ColumnChart.value,
                'title': 'Value of money in the bank during reporting month, by city',
                'y_axis_title': 'Money in the Bank',
                'x_axis_title': 'City/Town',
                'point_format': '{series.name}: {point.y:.0f}'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Value of money in the bank during reporting month, by city</b>')
            }
        ]
    },
    {
        'name': 'Value of S&C fund',
        'full_name': 'Value of S&C fund',
        'indicator': SavingsAndCreditIndicatorEnum.SCGFundEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Value of S&C fund'
            },
            {
                'type': GraphTypeEnum.ColumnChart.value,
                'title': 'Value of S&C fund, by city',
                'y_axis_title': 'Value of S&C fund',
                'x_axis_title': 'City/Town',
                'point_format': '{series.name}: {point.y:.0f}'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Value of S&C fund, by city</b>')
            }
        ]
    },
    {
        'name': 'Ratio of on-time realization',
        'full_name': 'Ratio of on-time realization',
        'indicator': SavingsAndCreditIndicatorEnum.SCGOntimeEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Ratio of on-time realization'
            },
            {
                'type': GraphTypeEnum.ColumnChart.value,
                'title': 'Ratio of on-time realization, by city',
                'y_axis_title': 'Ratio of on-time realization',
                'x_axis_title': 'City/Town',
                'point_format': '{series.name}: {point.y:.2f}%'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Ratio of on-time realization, by city</b>')
            }
        ]
    }
]
