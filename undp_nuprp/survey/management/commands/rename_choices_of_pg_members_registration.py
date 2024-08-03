from django.core.management.base import BaseCommand

from undp_nuprp.survey.models.entity.answer import Answer
from undp_nuprp.survey.models.entity.question import Question

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Renaming Bangla for choice: Earth/sand/semi pucca floor')
        choice_name = 'Earth/sand/semi pucca floor'
        _answer = Answer.objects.filter(text=choice_name).last()
        _answer.text_bd = 'মাটি/বালু মাটি/আধা পাকা মেঝে'
        _answer.save()

        print('Successfully renamed to : মাটি/বালু মাটি/আধা পাকা মেঝে')

        print("Updating next question of 2.4 for the options: 'Do not know', 'Never attended school'")

        _answers = Answer.objects.filter(question__question_code='2.4',
                                         text__in=['Do not know', 'Never attended school'])

        _question_2_6 = Question.objects.filter(question_code='2.6').last()

        for _answer in _answers:
            _answer.next_question = _question_2_6
            _answer.save()

        print('Successfully updated')

        print('Renaming Bangla for choice: কিন্ডারগার্টেন/নার্সারি/প্লেগ্র্রুপ/মক্তব')
        Answer.objects.filter(text_bd='কিন্ডারগার্টেন/নার্সারি/প্লেগ্র্রুপ/মক্তব').update(
            text_bd='কিন্ডারগার্টেন/নার্সারি/প্লেগ্রুপ/মক্তব')
        print('Successfully updated')