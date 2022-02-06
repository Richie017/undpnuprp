"""
    Created by tareq on 3/22/17
"""
from undp_nuprp.reports.config.survey_indicators_table import get_table_headers
from undp_nuprp.reports.utils.enums.graph_types import GraphTypeEnum, DataTableConfigEnum
from undp_nuprp.reports.utils.enums.household_survey_indicator import HouseholdSurveyIndicatorEnum

__author__ = 'Tareq'

household_survey_indicators = [
    {
        'name': 'Gender of HH head',
        'indicator': HouseholdSurveyIndicatorEnum.GenderIndicator.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.PieChart.value,
                'title': 'Gender of HH head, all cities',
                'point_format': '{point.y:.0f} <b>({point.percentage:.2f}%)</b>',
                # Definition of title
                'definition': '<b>House Hold:</b> A person living alone in a dwelling unit shall be considered as the head of that\
                 household. In a household consisting of a group of persons, a member is treated as the head whom\
                  the other members acknowledge to be so. Generally, the eldest male or female earner of the \
                  household is considered to be the head of the household. (Population Census, BBS)'
            },
            {
                'type': GraphTypeEnum.StackedColumnChart.value,
                'title': 'Gender of HH head',
                # Definition of title
                'definition': '<b>House Hold:</b> A person living alone in a dwelling unit shall be considered as the head of that\
                 household. In a household consisting of a group of persons, a member is treated as the head whom\
                  the other members acknowledge to be so. Generally, the eldest male or female earner of the \
                  household is considered to be the head of the household. (Population Census, BBS)',

                'y_axis_title': '% of Household',
                'x_axis_title': 'City Corporation / Pourashava',
                'point_format': '{series.name}: {point.y:.2f}%',
                'config': {
                    'yAxis': {
                        'max': 100, 'min': 0
                    }
                }
            },
            {
                "type": DataTableConfigEnum.DataTable.value,
                "title": "Percentage of male, female and hijra-headed households"
            }
        ]
    },
    {
        'name': 'Employment status of HH head',
        'indicator': HouseholdSurveyIndicatorEnum.EmploymentIndicator.value,
        'graph_types': [
            # {
            #     'type': GraphTypeEnum.PieChart.value,
            #     'title': 'Employment status of HH head, all cities',
            #     'point_format': '{point.y:.0f} <b>({point.percentage:.2f}%)</b>',
            #     # Definition of title
            #     'definition': '<b>House Hold:</b> A person living alone in a dwelling unit shall be considered as the head of that\
            #      household. In a household consisting of a group of persons, a member is treated as the head whom\
            #       the other members acknowledge to be so. Generally, the eldest male or female earner of the \
            #       household is considered to be the head of the household. (Population Census, BBS)'
            # },
            {
                'type': GraphTypeEnum.StackedColumnChart.value,
                'title': 'Employment status of HH head',
                'y_axis_title': '% of Household',
                'x_axis_title': 'City Corporation / Pourashava',
                'point_format': '{series.name}: {point.y:.2f}%',
                # Definition of title
                'definition': '<b>House Hold:</b> A person living alone in a dwelling unit shall be considered as the head of that\
                 household. In a household consisting of a group of persons, a member is treated as the head whom\
                  the other members acknowledge to be so. Generally, the eldest male or female earner of the \
                  household is considered to be the head of the household. (Population Census, BBS)',
                'config': {
                    'yAxis': {
                        'max': 100, 'min': 0
                    }
                }
            },
            {
                "type": DataTableConfigEnum.DataTable.value,
                "title": "Employment status of household head"
            }
        ]
    },
    {
        'name': 'Education attainment of HH head',
        'indicator': HouseholdSurveyIndicatorEnum.EducationalIndicator.value,
        'graph_types': [
            # {
            #     'type': GraphTypeEnum.PieChart.value,
            #     'title': 'Level of education attained by HH head, all cities',
            #     'point_format': '{point.y:.0f} <b>({point.percentage:.2f}%)</b>',
            #     # Definition of title
            #     'definition': '<b>House Hold:</b> A person living alone in a dwelling unit shall be considered as the head of that\
            #      household. In a household consisting of a group of persons, a member is treated as the head whom\
            #       the other members acknowledge to be so. Generally, the eldest male or female earner of the \
            #       household is considered to be the head of the household. (Population Census, BBS)'
            # },
            {
                'type': GraphTypeEnum.StackedColumnChart.value,
                'title': 'Level of education attained by HH head',
                'y_axis_title': '% of Household',
                'x_axis_title': 'City Corporation / Pourashava',
                'point_format': '{series.name}: {point.y:.2f}%',
                # Definition of title
                'definition': '<b>House Hold:</b> A person living alone in a dwelling unit shall be considered as the head of that\
                 household. In a household consisting of a group of persons, a member is treated as the head whom\
                  the other members acknowledge to be so. Generally, the eldest male or female earner of the \
                  household is considered to be the head of the household. (Population Census, BBS)',
                'config': {
                    'yAxis': {
                        'max': 100, 'min': 0
                    }
                }
            },
            {
                "type": DataTableConfigEnum.DataTable.value,
                "title": "Mean level of school attended by household head"
            }
        ]
    },
    {
        'name': 'HH dependents',
        'indicator': HouseholdSurveyIndicatorEnum.DependentMemberIndicator.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.StackedColumnChart.value,
                'title': 'HH dependents',
                'y_axis_title': '% of Household',
                'x_axis_title': 'City Corporation / Pourashava',
                'point_format': '{series.name}: {point.y:.2f}%',
                # Definition of title
                'definition': '<b>House Hold:</b> A person living alone in a dwelling unit shall be considered as the head of that\
                 household. In a household consisting of a group of persons, a member is treated as the head whom\
                  the other members acknowledge to be so. Generally, the eldest male or female earner of the \
                  household is considered to be the head of the household. (Population Census, BBS)'
            }
        ]
    },
    {
        'name': 'Mean HH size',
        'full_name': 'Mean household size',
        'indicator': HouseholdSurveyIndicatorEnum.HouseholdSizeIndicator.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.FlatHtml.value,
                'title': 'Mean HH size, all cities',
                # Definition of title
                'definition': '<b>House Hold:</b> A person living alone in a dwelling unit shall be considered as the head of that\
                 household. In a household consisting of a group of persons, a member is treated as the head whom\
                  the other members acknowledge to be so. Generally, the eldest male or female earner of the \
                  household is considered to be the head of the household. (Population Census, BBS)'
            },
            {
                "type": DataTableConfigEnum.DataTable.value,
                "title": "Mean household size"
            }
        ]
    },
    {
        'name': 'Vulnerability (based on multidimensional poverty index)',
        'indicator': HouseholdSurveyIndicatorEnum.HouseholdMPIIndicator.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.ScatterChart.value,
                'title': 'Vulnerability (based on multidimensional poverty index), all cities',
                'y_axis_title': '% of Household',
                'x_axis_title': 'MPI Score',
                'x_axis_description': 'A household is said to be multi-dimensionally poor if it score 30 points or more. The higher the score, the higher their level of poverty',
                'decimal_places': 2
            },
            {
                'type': GraphTypeEnum.StackedColumnChart.value,
                'title': 'Vulnerability (based on multidimensional poverty index)',
                'y_axis_title': '% of Household',
                'x_axis_title': 'City Corporation / Pourashava',
                'point_format': '{series.name}: {point.y:.2f}%',
                'config': {
                    'yAxis': {
                        'max': 100, 'min': 0
                    }
                }
            }
        ]
    },
    {
        'name': 'Deprivation, by indicator',
        'indicator': HouseholdSurveyIndicatorEnum.DeprivedHouseholdIndicator.value,
        'graph_types': [
            # {
            #     'type': GraphTypeEnum.StackedColumnChart.value,
            #     'title': 'Deprivation, by indicator',
            #     'y_axis_title': '% of Deprived Household',
            #     'x_axis_title': 'Indicators',
            #     'point_format': '{series.name}: {point.y:.2f}'
            # },
            {
                'type': GraphTypeEnum.HorizontalBarChart.value,
                'title': 'Deprivation, by indicator, all cities',
                'y_axis_title': '% of Deprived Household',
                'x_axis_title': 'Indicators',
                'point_format': '{series.name}: {point.y:.2f}'
            },
            {
                "type": DataTableConfigEnum.DataTable.value,
                "title": "Percentage of households deprived by indicator"
            }
        ]
    },
    {
        'name': 'MPI v’s HH Characteristics',
        'indicator': HouseholdSurveyIndicatorEnum.MPIvsCharacteristicIndicator.value,
        'graph_types': [
            {
                'type': GraphTypeEnum.ColumnChart.value,
                'title': 'Mean MPI score, by household characteristics, all cities',
                'y_axis_title': 'Avg MPI Score',
                'x_axis_title': 'Household Type',
                'point_format': '{series.name}: {point.y:.2f}'
            }
        ]
    }
]
