from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

from dynamic_survey.models.design.dynamic_survey import DynamicSurvey

__author__ = 'Razon'


@decorate(is_object_context,
          route(route='library-questions', group='Dynamic Survey', group_order=5, module=ModuleEnum.Administration,
                display_name="Library Questions", item_order=2))
class LibraryQuestions(DynamicSurvey):
    class Meta:
        proxy = True
        app_label = 'dynamic_survey'
