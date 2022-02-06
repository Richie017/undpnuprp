"""This module handles the view when view survey button is clicked """

from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.core.generics.views.restore_view import GenericRestoreView

from dynamic_survey.models.design.dynamic_survey import DynamicSurvey


@decorate(override_view(model=DynamicSurvey, view=ViewActionEnum.Restore))
class DynamicSurveyViewerView(GenericRestoreView):
    """This class is extended by `GenericRestoreView` class and simply overrides the `get` method
       of the above class. As restore button is not used in the view so we can safely override
       the generic view and use it on our custom purpose.
    """

    def get(self, request, *args, **kwargs):
        """
        This method simply takes in the get request for the view survey button and redirects
        the url to the view page of the corresponding survey

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
        success_url = "/" + root_url + "/" + "#/viewer/" + survey_id
        return self.render_json_response({
            'message': 'Request completed successfully.',
            'success': True,
            'load': 'ajax',
            'success_url': success_url,
        })
