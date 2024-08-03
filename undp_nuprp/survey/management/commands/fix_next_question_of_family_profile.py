from django.core.management import BaseCommand
from django.db import transaction

from blackwidow.engine.extensions import Clock
from undp_nuprp.survey.models import Question, Answer


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            q_codes = ['6.12', '6.13', '6.14', '6.15', '6.16', '6.17']
            questions = Question.objects.filter(question_code__in=q_codes).order_by('order').prefetch_related('answers')
            answers = []
            count = 1
            max = questions.count() - 1
            current_timestamp = Clock.timestamp()
            for ques in questions:
                for a in ques.answers.all():
                    if count <= max:
                        a.next_question_id = questions[count].id
                        a.last_updated = current_timestamp
                        current_timestamp += 1
                        answers.append(a)
                count += 1
            Answer.objects.bulk_update(answers, batch_size=200)
