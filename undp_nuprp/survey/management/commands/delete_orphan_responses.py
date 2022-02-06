"""
    Created by tareq on 8/28/19
"""
from datetime import datetime

from django.core.management import BaseCommand

from undp_nuprp.survey.models import QuestionResponse, SectionResponse

__author__ = "Tareq"


class Command(BaseCommand):
    def handle(self, *args, **options):
        current_timestamp = datetime.now().timestamp() * 1000
        deletable_question_responses = QuestionResponse.objects.filter(
            section_response__survey_response__is_deleted=True) | QuestionResponse.objects.filter(
            section_response__survey_response__isnull=True)

        deletable_question_responses.update(is_deleted=True, deleted_level=1, last_updated=current_timestamp)

        deletable_section_responses = SectionResponse.objects.filter(
            survey_response__is_deleted=True) | SectionResponse.objects.filter(survey_response__isnull=True)

        deletable_section_responses.update(is_deleted=True, deleted_level=1, last_updated=current_timestamp)
        print("done")
