from django.core.management.base import BaseCommand

from undp_nuprp.survey.models.entity.question import Question

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        question_code = input('Enter question code to set required status: ')
        print(question_code)
        question = Question.objects.filter(question_code=question_code).first()

        if not question:
            print('Question does not exist!')
            return

        print(question.text)
        print('Required status: {}'.format('True' if question.is_required else 'False'))
        updated_status = input('Update status (True/False): ')
        question.is_required = True if updated_status.lower() == 'true' else False
        question.save()

        print('Successfully updated question code')
