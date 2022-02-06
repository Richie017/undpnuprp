from datetime import datetime

from blackwidow.core.generics.views.advanced_export_view import AdvancedGenericExportView
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.exceptions import BWException
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from dynamic_survey.models import DynamicSurveyResponse
from dynamic_survey.models.response.dynamic_survey_response_generated_file import DynamicSurveyResponseGeneratedFile

__author__ = 'Ziaul Haque'


@decorate(override_view(model=DynamicSurveyResponse, view=ViewActionEnum.AdvancedExport))
class DynamicSurveyResponseExportView(AdvancedGenericExportView):

    def start_background_worker(self, request, organization, export_file_name, *args, **kwargs):
        _name = self.generate_file_name()

    def generate_file_name(self):
        dest_filename = self.model.get_export_file_name()
        survey = self.request.GET.get('survey', None)
        year = self.request.GET.get('year', None)
        month = self.request.GET.get('month', None)

        month_number = datetime.strptime(month, "%B").month

        generated_file = DynamicSurveyResponseGeneratedFile.objects.using(
            BWDatabaseRouter.get_export_database_name()
        ).filter(year=year, month=month_number, survey_id=survey, file__isnull=False).first()
        if not generated_file:
            raise BWException("Dynamic Survey Response export file does not exist.")

        return "{0}_{1}_{2}_{3}".format(survey, dest_filename, month, year)
