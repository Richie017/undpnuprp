"""
Created by tareq on 8/14/17
"""
from django.core.management.base import BaseCommand

from undp_nuprp.nuprp_admin.utils.enums.question_type_enum import QuestionTypeEnum
from undp_nuprp.survey.models.response.question_response import QuestionResponse

__author__ = 'Tareq'


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        duplicate_questions = QuestionResponse.objects.exclude(
            question__question_type=QuestionTypeEnum.MultipleSelectInput.value).order_by('-date_created').values(
            'section_response_id', 'question_id')
