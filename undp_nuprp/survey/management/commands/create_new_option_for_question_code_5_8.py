from django.core.management.base import BaseCommand
from django.db.models.aggregates import Max

from blackwidow.core.models.organizations.organization import Organization
from undp_nuprp.nuprp_admin.utils.enums.answer_type_enum import AnswerTypeEnum
from undp_nuprp.nuprp_admin.utils.enums.question_type_enum import QuestionTypeEnum
from undp_nuprp.survey.models.entity.answer import Answer
from undp_nuprp.survey.models.entity.question import Question

__author__ = 'Rafi'


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Creating/Updating new option for the question *Does your household have the following assets or facilities?(5.8)*')
        _answer = Answer.objects.filter(answer_code='5.8.11')
        if _answer.exists():
            _answer = _answer.first()
            _answer.text = 'Others/No Assets'
            _answer.text_bd = 'অন্যান্য/কোনো সম্পদ নেই'
            _answer.answer_type = AnswerTypeEnum.MultipleSelectInput.value
            _answer.save()

            _question = Question.objects.filter(question_code='5.8').first()
            _question.question_type = QuestionTypeEnum.MultipleSelectInput.value
            _question.save()
        else:
            _answer = Answer(
                organization=Organization.objects.first(),
                text='None of the above',
                text_bd='উপরের কোনটিই নয়',
                answer_type='multiple',
                answer_code='5.8.11'
            )
            _question = Question.objects.filter(question_code='5.8').first()
            _next_question = Question.objects.filter(question_code='5.9').first()
            _max_order = Answer.objects.filter(question_id=_question.pk).aggregate(Max('order'))['order__max']

            _answer.question = _question
            _answer.next_question = _next_question
            _answer.order = _max_order + 1
            _answer.save()

        print('Successfully added option: None of the above')
