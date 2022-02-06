from django.utils.safestring import mark_safe

from undp_nuprp.reports.utils.enums.graph_types import DataTableConfigEnum
from undp_nuprp.reports.utils.enums.nutrition_indicator import NutritionIndicatorEnum

nutrition_indicators = [
    {
        'name': 'Nutrition Registration for reporting month',
        'full_name': 'Nutrition Registration for reporting month',
        'indicator': NutritionIndicatorEnum.NutritionRegistration.value,
        'graph_types': [
            {
                'type': DataTableConfigEnum.DataTable.value + '1',
                'title': mark_safe('<b>Nutrition Registration of Pregnant Women by age groups (city-wise)</b>')
            },
            {
                'type': DataTableConfigEnum.DataTable.value + '2',
                'title': mark_safe('<b>Nutrition Registration of Lactating Mothers by age groups (city-wise)</b>')
            },
            {
                'type': DataTableConfigEnum.DataTable.value + '3',
                'title': mark_safe('<b>Nutrition Registration of Child (0-6) Months by Sex (city-wise)</b>')
            },
            {
                'type': DataTableConfigEnum.DataTable.value + '4',
                'title': mark_safe('<b>Nutrition Registration of Child (7-24) Months by Sex (city-wise)</b>')
            }
        ]
    },
    {
        'name': 'Nutrition Conditional Food Transfer for reporting month',
        'full_name': 'Nutrition Conditional Food Transfer for reporting month',
        'indicator': NutritionIndicatorEnum.NutritionConditionalFoodTransfer.value,
        'graph_types': [
            {
                'type': DataTableConfigEnum.DataTable.value + '1',
                'title': mark_safe(
                    '<b>Nutrition Conditional Food Transfer of Pregnant Women by age groups (city-wise)</b>')
            },
            {
                'type': DataTableConfigEnum.DataTable.value + '2',
                'title': mark_safe(
                    '<b>Nutrition Conditional Food Transfer of Lactating Mothers by age groups (city-wise)</b>')
            },
            {
                'type': DataTableConfigEnum.DataTable.value + '3',
                'title': mark_safe(
                    '<b>Nutrition Conditional Food Transfer of Child (0-6) Months by Sex (city-wise)</b>')
            },
            {
                'type': DataTableConfigEnum.DataTable.value + '4',
                'title': mark_safe(
                    '<b>Nutrition Conditional Food Transfer of Child (7-24) Months by Sex (city-wise)</b>')
            }
        ]
    },
]
