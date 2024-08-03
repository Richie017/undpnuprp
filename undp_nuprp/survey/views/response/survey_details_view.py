from django.urls.base import reverse

from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.survey.models.entity.survey import Survey
from undp_nuprp.survey.models.export.survey_response_generated_file import SurveyResponseGeneratedFile
from blackwidow.core.generics.views.details_view import GenericDetailsView

__author__ = "Shama"


@decorate(override_view(model=Survey, view=ViewActionEnum.Details))
class SurveyDetailsView(GenericDetailsView):
    def get_template_names(self):
        return ['survey_response/survey_response_details.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['export_link'] = reverse(SurveyResponseGeneratedFile.get_route_name(ViewActionEnum.Manage))
        return context
