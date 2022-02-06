from django.utils.safestring import mark_safe

from undp_nuprp.reports.utils.enums.graph_types import GraphTypeEnum, DataTableConfigEnum
from undp_nuprp.reports.utils.enums.pg_hh_indicator import PGHHIndicatorEnum

__author__ = "Shama"

pg_hh_information_indicators = [
    {
        'name': 'Mean HH Size',
        'full_name': 'Mean HH Size',
        'indicator': PGHHIndicatorEnum.HHMeanSizeEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': mark_safe('<b>Mean HH size (all cities)</b>')
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Mean HH size, by city</b>')
            }
        ]
    },
    {
        'name': 'Vulnerability (based on multidimensional poverty index)',
        'full_name': 'Vulnerability (based on multidimensional poverty index)',
        'indicator': PGHHIndicatorEnum.HHVulnerabilityEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.ColumnChart.value,
                'title': '% of PG HHs by sum of weighted deprivations (all cities)',
                'y_axis_title': '% of PG HHs',
                'x_axis_title': 'Sum of weighted deprivations',
                'point_format': '{series.name}: {point.y:.0f}'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>MPI score of PG members, by city</b>')
            }
        ]
    },
    {
        'name': 'Deprivation, by indicator',
        'full_name': 'Deprivation, by indicator',
        'indicator': PGHHIndicatorEnum.HHDeprivationEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.HorizontalBarChart.value,
                'title': '% of HHs deprived, by indicator (all cities)',
                'y_axis_title': '% of Deprived Household',
                'x_axis_title': 'Indicators',
                'point_format': '{series.name}: {point.y:.0f}'
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>% of HHs deprived, by indicator, by city</b>')
            }
        ]
    },
    {
        'name': 'MPI vs HH characteristics',
        'full_name': 'MPI vs HH characteristics',
        'indicator': PGHHIndicatorEnum.MPICharacteristicsEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.StackedColumnChart.value,
                'title': 'MPI score by type of HH (all cities)',
                'x_axis_title': 'Legends',
                'y_axis_title': '% of HH',
                'point_format': '{series.name}: {point.y:.0f}%',
                'config': {
                    'yAxis': {
                        'max': 100, 'min': 0
                    }
                }
            },
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>% of HH MPI poor (20 and above)</b>')
            }

        ]
    },
    {
        'name': 'HH dependents',
        'full_name': 'HH dependents',
        'indicator': PGHHIndicatorEnum.HHDependentsEnum.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.StackedColumnChart.value,
                'title': 'HH dependents',
                'y_axis_title': '% of Household',
                'x_axis_title': 'City Corporation/Town',
                'point_format': '{series.name}: {point.y:.0f}%',
                'config': {
                    'yAxis': {
                        'max': 100, 'min': 0
                    }
                }
            }
        ]
    },
    {
        'name': 'HH composition',
        'full_name': 'HH composition',
        'indicator': PGHHIndicatorEnum.HHCompositionEnum.value,
        'graph_types': [
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>HH composition</b>')
            }
        ]
    }
]
