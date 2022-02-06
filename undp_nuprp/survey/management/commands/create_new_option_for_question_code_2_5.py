from django.core.management.base import BaseCommand
from django.db.models.aggregates import Max

from blackwidow.core.models.organizations.organization import Organization
from undp_nuprp.survey.models.entity.answer import Answer
from undp_nuprp.survey.models.entity.question import Question

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Creating new option for the question *Highest class completed at that level(2.5)*')
        _answer = Answer(
            organization=Organization.objects.first(),
            text='kindergarten/nursery/playgroup/Moktab',
            text_bd='কিন্ডারগার্টেন/নার্সারি/প্লেগ্র্রুপ/মক্তব',
            answer_type='single',
            answer_code='2.5.17'
        )
        _question = Question.objects.filter(question_code='2.5').first()
        _next_question = Question.objects.filter(question_code='2.6').first()
        _max_order = Answer.objects.filter(question_id=_question.pk).aggregate(Max('order'))['order__max']

        _answer.question = _question
        _answer.next_question = _next_question
        _answer.order = _max_order + 1
        _answer.save()

        print('Successfully added options: kindergarten/nursery/playgroup/Moktab')
