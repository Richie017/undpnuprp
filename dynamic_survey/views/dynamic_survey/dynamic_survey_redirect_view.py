"""This module handles the view when edit survey button is clicked """
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.core.generics.views.edit_view import GenericEditView

from dynamic_survey.models.design.dynamic_survey import DynamicSurvey


@decorate(override_view(model=DynamicSurvey, view=ViewActionEnum.Edit))
class DynamicSurveyRedirectView(GenericEditView):
    """This class is extended by `GenericEditView` class and simply overrides the `get` method
       of the above class.
    """

    def get(self, request, *args, **kwargs):
        """
        This method simply takes in the get request for the edit survey button and redirects
        the url to the editing page of the corresponding survey

        :param request: the request object
        :type request: `HttpRequest` object
        :param args: variable number of positional arguments
        :type args: variable number of positional arguments
        :param kwargs: variable number of keyword arguments
        :type kwargs: variable number of keyword arguments
        :return: json response to redirect to the `success_url`
        :rtype: json response
        """
        root_url = DynamicSurvey._registry[DynamicSurvey.__name__]['route']['route']
        survey_id = self.request.get_full_path().rsplit('/', 1)[-1]
        success_url = "/" + root_url + "/" + "#/builder/" + survey_id
        return self.render_json_response({
            'message': 'Request completed successfully.',
            'success': True,
            'load': 'ajax',
            'success_url': success_url,
        })
