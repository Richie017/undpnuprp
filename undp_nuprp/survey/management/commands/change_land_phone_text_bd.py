from django.core.management.base import BaseCommand

from undp_nuprp.survey.models.entity.answer import Answer

__author__ = 'Rafi'


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Creating bangla for the option *Land phone(5.8.5)*')
        _answer = Answer.objects.filter(answer_code='5.8.5').first()

        _answer.text_bd = 'টেলিফোন'
        _answer.save()

        print('Successfully change bangla option: টেলিফোন')
