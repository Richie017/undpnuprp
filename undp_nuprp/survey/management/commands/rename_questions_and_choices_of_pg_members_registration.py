from django.core.management.base import BaseCommand

from undp_nuprp.survey.models.entity.answer import Answer
from undp_nuprp.survey.models.entity.question import Question

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Renaming question of code: 5.1')
        _q_code = '5.9'
        _question = Question.objects.filter(question_code=_q_code).last()
        _question.text = 'Has any child (<=5 years) in the household died after birth within that last five years?'
        _question.text_bd = 'গত পাঁচ বছরে পরিবারের মধ্যে কোনও শিশু (<= 5 বছর) কি জন্মের পর মারা গিয়েছিল?'
        _question.save()

        print('Question of code:5.1 has been renamed successfully')

        print('Renaming option "Earth/sand" to Earth/sand/semi pucca floor')
        _answer = Answer.objects.filter(text='Earth/sand').filter(answer_code='5.2.1').last()
        _answer.text = 'Earth/sand/semi pucca floor'
        _answer.text_bd = 'আধা পাকা মেঝে'
        _answer.save()
        print('Successfully renamed')

        print('Renaming option of question code: 5.8')
        _answer = Answer.objects.filter(question__question_code='5.8').filter(text='Refrigerator').last()
        _answer.text = 'Functional refrigerator'
        _answer.text_bd = 'কার্যকরী ফ্রিজ'
        _answer.save()

        _answer = Answer.objects.filter(question__question_code='5.8').filter(text='Television').last()
        _answer.text = 'Smart/ Led TV'
        _answer.text_bd = 'স্মার্ট/ এলইডি টেলিভিশন'
        _answer.save()

        _answer = Answer.objects.filter(question__question_code='5.8').filter(text='Mobile Phone').last()
        _answer.text = 'Smart mobile phone'
        _answer.text_bd = 'স্মার্ট মোবাইল ফোন'
        _answer.save()
        print('Successfully renamed question code: 5.8')
