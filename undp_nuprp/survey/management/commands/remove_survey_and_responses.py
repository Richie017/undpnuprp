from django.core.management.base import BaseCommand
from django.db import transaction

from dynamic_survey.models.design.dynamic_survey import DynamicSurvey
from dynamic_survey.models.response.dynamic_survey_response import DynamicSurveyResponse
from undp_nuprp.survey.models.response.survey_response import SurveyResponse

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Removing PG member survey response
        print('Deleting survey response')
        _survey_response_ids = [382888, 382889, 382890]
        with transaction.atomic():
            SurveyResponse.objects.filter(id__in=_survey_response_ids).delete()
            print('Successfully deleted')

            # Removing dynamic survey and responses
            _survey_ids = [30, 31, 33, 29, 10, 9, 7, 25, 28, 27]

            for _id in _survey_ids:
                _survey = DynamicSurvey.objects.filter(id=_id).first()
                if _survey:
                    print('Deleting survey: {} and its responses'.format(_survey.name))
                    DynamicSurveyResponse.objects.filter(survey=_survey).delete()
                    DynamicSurvey.objects.filter(id=_id).delete()
                    print('Successfully deleted')
