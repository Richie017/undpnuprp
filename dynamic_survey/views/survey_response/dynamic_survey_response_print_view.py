from blackwidow.core.generics.views.printable_views.printable_details_view import GenericPrintableContentView
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from dynamic_survey.models import DynamicSurveyResponse
from dynamic_survey.views.survey_response.dynamic_survey_response_view_mixin import DynamicSurveyResponseViewMixin


@decorate(override_view(model=DynamicSurveyResponse, view=ViewActionEnum.Print))
class DynamicSurveyResponsePrintView(GenericPrintableContentView, DynamicSurveyResponseViewMixin):

    def get_context_data(self, **kwargs):
        context = super(DynamicSurveyResponsePrintView, self).get_context_data(**kwargs)
        context['model_meta']['sections'] = self.prepare_survey_data()
        return context

    def get_template_names(self):
        return ['survey_response/survey_response_printable_info.html']
