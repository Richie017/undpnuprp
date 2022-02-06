"""
Created by tareq on 5/25/17
"""
from django.urls.base import reverse

from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.survey.models.export.survey_response_generated_file import SurveyResponseGeneratedFile
from undp_nuprp.survey.models.response.survey_response import SurveyResponse

__author__ = 'Tareq'


@decorate(override_view(model=SurveyResponse, view=ViewActionEnum.Manage))
class SurveyResponseListView(GenericListView):
    def get_template_names(self):
        return ['survey_response/survey_response_list.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['export_link'] = reverse(SurveyResponseGeneratedFile.get_route_name(ViewActionEnum.Manage))
        return context
