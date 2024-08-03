"""
This module handles the view of the list of survey response
Created by tareq on 5/25/17
"""

from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.core.generics.views.list_view import GenericListView

from dynamic_survey.models.response.dynamic_survey_response import DynamicSurveyResponse

__author__ = 'Tareq'


@decorate(override_view(model=DynamicSurveyResponse, view=ViewActionEnum.Manage))
class SurveyResponseListView(GenericListView):
    """ This class simply overrides two methods of `GenericListView`  and determines the view of
        the list of survey response.
    """

    def get_context_data(self, **kwargs):
        """
        This method returns the context that the template is going to receive

        :param kwargs: variable number of keyword arguments
        :type kwargs: kwargs: variable number of keyword arguments
        :return: returns a dictionary that contains the context that the template is going to receive
        :rtype: dictionary
        """

        context = super().get_context_data(**kwargs)
        return context
