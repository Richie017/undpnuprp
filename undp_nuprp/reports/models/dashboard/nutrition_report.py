from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.managers.nutrition.nutrition_registration_indicator import \
    get_nutrition_registration_indicator_table_data_1, get_nutrition_registration_indicator_table_data_2, \
    get_nutrition_registration_indicator_table_data_3, get_nutrition_registration_indicator_table_data_4, \
    get_nutrition_conditional_food_transfer_indicator_table_data_1, \
    get_nutrition_conditional_food_transfer_indicator_table_data_2, \
    get_nutrition_conditional_food_transfer_indicator_table_data_3, \
    get_nutrition_conditional_food_transfer_indicator_table_data_4
from undp_nuprp.reports.models import Report
from undp_nuprp.reports.utils.enums.graph_types import DataTableConfigEnum
from undp_nuprp.reports.utils.enums.nutrition_indicator import NutritionIndicatorEnum


@decorate(is_object_context,
          route(route='nutrition-report', group='Local Economy Livelihood and Financial Inclusion ', group_order=3,
                module=ModuleEnum.Reports, display_name="Nutrition", item_order=6))
class NutritionReport(Report):
    class Meta:
        proxy = True
        app_label = 'reports'

    def build_report(self, from_time=None, to_time=None, indicator=None, graph_type=None, year=None, month=None):
        if indicator == NutritionIndicatorEnum.NutritionRegistration.value:
            if graph_type == DataTableConfigEnum.DataTable.value + '1':
                return get_nutrition_registration_indicator_table_data_1(from_time, to_time, year, month)
            if graph_type == DataTableConfigEnum.DataTable.value + '2':
                return get_nutrition_registration_indicator_table_data_2(from_time, to_time, year, month)
            if graph_type == DataTableConfigEnum.DataTable.value + '3':
                return get_nutrition_registration_indicator_table_data_3(from_time, to_time, year, month)
            if graph_type == DataTableConfigEnum.DataTable.value + '4':
                return get_nutrition_registration_indicator_table_data_4(from_time, to_time, year, month)
        if indicator == NutritionIndicatorEnum.NutritionConditionalFoodTransfer.value:
            if graph_type == DataTableConfigEnum.DataTable.value + '1':
                return get_nutrition_conditional_food_transfer_indicator_table_data_1(from_time, to_time, year, month)
            if graph_type == DataTableConfigEnum.DataTable.value + '2':
                return get_nutrition_conditional_food_transfer_indicator_table_data_2(from_time, to_time, year, month)
            if graph_type == DataTableConfigEnum.DataTable.value + '3':
                return get_nutrition_conditional_food_transfer_indicator_table_data_3(from_time, to_time, year, month)
            if graph_type == DataTableConfigEnum.DataTable.value + '4':
                return get_nutrition_conditional_food_transfer_indicator_table_data_4(from_time, to_time, year, month)
