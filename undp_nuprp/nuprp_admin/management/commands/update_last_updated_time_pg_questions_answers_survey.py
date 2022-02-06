"""
    Written by shuvro on 09/05/2019
"""
from django.core.management.base import BaseCommand

from undp_nuprp.survey.models.entity.answer import Answer
from undp_nuprp.survey.models.entity.question import Question
from undp_nuprp.survey.models.entity.survey import Survey

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        questions = Question.objects.all()
        answers = Answer.objects.all()
        surveys = Survey.objects.all()

        print('Updating last updated time of questions')

        for question in questions:
            question.save()

        print('Question updated successfully')

        print('Updating last updated time of answers')
        for answer in answers:
            answer.save()
        print('Answer updated successfully')

        print('Updating last updated time of PG survey')
        for survey in surveys:
            survey.save()
        print('PG survey updated successfully')


