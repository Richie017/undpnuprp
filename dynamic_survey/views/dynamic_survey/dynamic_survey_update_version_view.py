"""This module handles the view when upgrade survey version button is clicked """
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.core.generics.views.deactivate_view import GenericDeactivateView
from blackwidow.core.models import ErrorLog
from django.db import transaction

from dynamic_survey.enums.dynamic_survey_status_enum import DynamicSurveyStatusEnum
from dynamic_survey.models.design.dynamic_survey import DynamicSurvey
from dynamic_survey.models.design.dynamic_survey_group import DynamicSurveyGroup


@decorate(override_view(model=DynamicSurvey, view=ViewActionEnum.Deactivate))
class DynamicSurveyUpgradeView(GenericDeactivateView):
    """This class is extended by `GenericRejectView` class and simply overrides the `get` method
       of the above class. As reject button is not used in the view so we can safely override
       the generic view and use it on our custom purpose. This class creates exactly a same
       copy of the survey and saves it as a new draft version of the corresponding survey.
    """

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        """
        This method simply takes in the get request for the upgrade survey button and redirects
        the url to the builder page of the newly created survey. In the mean time it performs the following tasks:
        1. Creates an exact copy of the current survey and saves it as a new draft
        version of the survey.
        2. Updates meta information of `DynamicSurveyGroup` class.
        3. Creates approval action for the new survey.


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
        # Create The new Survey Draft with existing copy Here and update the version and redirect to that edit url
        success_url = "/" + root_url + "/"
        survey_id = self.request.get_full_path().rsplit('/', 1)[-1]

        current_survey = DynamicSurvey.objects.filter(id=survey_id).first()
        survey = DynamicSurveyGroup.objects.filter(id=current_survey.survey_id).first()
        if current_survey and survey:
            survey.total_versions += 1

            data = dict()
            data['user'] = self.request.user
            data['name'] = current_survey.name
            data['status'] = DynamicSurveyStatusEnum.Draft.value
            data['version'] = survey.total_versions
            data['survey'] = current_survey.survey
            data['detail_link'] = current_survey.detail_link
            data['body'] = current_survey.body
            data['description'] = current_survey.description
            data['summary'] = current_survey.summary
            data['asset_type'] = current_survey.asset_type
            data['kpi_asset_uid'] = current_survey.kpi_asset_uid
            data['tags'] = current_survey.tags
            new_survey = DynamicSurvey(**data)

            try:
                survey.save()
                new_survey.save()
            except Exception as e:
                ErrorLog.log(exp=e)

            new_survey_id = new_survey.id
            success_url = "/" + root_url + "/" + "#/builder/" + str(new_survey_id)
        return self.render_json_response({
            'message': 'Request completed successfully.',
            'success': True,
            'load': 'ajax',
            'success_url': success_url,
        })
