""" This module handles the view of survey response details """

from blackwidow.core.generics.views.details_view import GenericDetailsView
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from dynamic_survey.models.response.dynamic_survey_response import DynamicSurveyResponse
from dynamic_survey.views import DynamicSurveyResponseViewMixin

__author__ = 'Tareq'


@decorate(override_view(model=DynamicSurveyResponse, view=ViewActionEnum.Details))
class SurveyResponseDetailsView(DynamicSurveyResponseViewMixin, GenericDetailsView):
    """ This class simply overrides two methods of `GenericDetailsView`  and determines the view of
        survey response details.
    """

    def get_template_names(self):
        """

        :return: list of template names  that the view is going to provide the first one ot gets
        :rtype: list of string
        """

        return [
            'survey_response/details.html'
        ]

    def get_context_data(self, **kwargs):
        """
        This method returns the context that the template is going to receive

        :param kwargs: variable number of keyword arguments
        :type kwargs: kwargs: variable number of keyword arguments
        :return: returns a dictionary that contains the context that the template is going to receive
        :rtype: dictionary
        """

        context = super(SurveyResponseDetailsView, self).get_context_data(**kwargs)
        context['model_meta']['sections'] = self.prepare_survey_data()
        context['model_meta']['properties']['detail_title'] = "Survey Response"
        return context