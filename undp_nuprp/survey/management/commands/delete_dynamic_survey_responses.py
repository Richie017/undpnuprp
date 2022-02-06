from django.core.management.base import BaseCommand
from django.db import transaction

from dynamic_survey.enums.dynamic_survey_status_enum import DynamicSurveyStatusEnum
from dynamic_survey.models.design.dynamic_survey import DynamicSurvey
from dynamic_survey.models.response.dynamic_question_response import DynamicQuestionResponse
from dynamic_survey.models.response.dynamic_section_response import DynamicSectionResponse
from dynamic_survey.models.response.dynamic_survey_response import DynamicSurveyResponse

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            # Removing dynamic survey and responses
            _survey_ids = [13, 16, 21, 24, 35, 36, 34, 38, 40, 41, 43, 44, 46, 45, 47, 37, 51, 58, 50, 49, 54, 55, 39,
                           57, 58, 59, 56, 61, 60, 62, 63, 64, 65, 66, 67, 75, 74, 76, 77, 78, 79, 81, 90, 92, 95]

            _survey_ids.extend(list(
                DynamicSurvey.objects.filter(status=DynamicSurveyStatusEnum.Draft.value).values_list('pk', flat=True)))

            for _id in _survey_ids:
                _survey = DynamicSurvey.objects.filter(id=_id).first()
                if _survey:
                    total, items = DynamicQuestionResponse.objects.filter(
                        section_response__survey_response__survey_id=_id).delete()
                    print(
                        'Total {} question responses has deleted associated with the dynamic survey: #{}'.format(total,
                                                                                                                 _id))

                    total, items = DynamicSectionResponse.objects.filter(survey_response__survey_id=_id).delete()
                    print('Total {} section responses has deleted associated with the dynamic survey: #{}'.format(total,
                                                                                                                  _id))

                    total, items = DynamicSurveyResponse.objects.filter(survey_id=_id).delete()
                    print('Total {} survey responses has deleted associated with the dynamic survey: #{}'.format(total,
                                                                                                                 _id))

                    DynamicSurvey.objects.filter(id=_id).delete()
                    print('Survey name: {} has deleted successfully'.format(_survey.name))
