from django.core.management.base import BaseCommand

from blackwidow.core.models import *
from undp_nuprp.survey.models import *

__author__ = 'Ziaul Haque'


class Command(BaseCommand):
    help = "Household Survey and associated Sections, Questions Soft deletion Command"

    def handle(self, *args, **options):
        _user = ConsoleUser.objects.first()

        deletable_questions = Question.objects.filter(section__survey__name='Household Survey Questionnaire')
        _index = 1
        for question in deletable_questions:
            question.soft_delete(user=_user, force_delete=True)
            _index += 1
        print("Total Question Deleted: %d" % _index)

        deletable_sections = Section.objects.filter(survey__name='Household Survey Questionnaire')
        _index = 1
        for section in deletable_sections:
            section.soft_delete(user=_user, force_delete=True)
            _index += 1
        print("Total Section Deleted: %d" % _index)

        deletable_surveys = Survey.objects.filter(name='Household Survey Questionnaire')
        _index = 1
        for survey in deletable_surveys:
            survey.soft_delete(user=_user, force_delete=True)
            _index += 1
        print("Total Survey Deleted: %d" % _index)
