from django.core.management import BaseCommand
from django.db.models import Func, F, Value

from blackwidow.engine.extensions import Clock
from undp_nuprp.survey.models import Question, Answer


class Command(BaseCommand):
    def handle(self, *args, **options):
        current_timestamp = Clock.timestamp()

        Question.objects.filter(text_bd__contains='হিজড়া').update(
            text_bd=Func(F('text_bd'), Value('হিজড়া'), Value('তৃতীয় লিঙ্গ'), function='replace'),
            last_updated=current_timestamp
        )

        Answer.objects.filter(text_bd__contains='হিজড়া').update(
            text_bd=Func(F('text_bd'), Value('হিজড়া'), Value('তৃতীয় লিঙ্গ'), function='replace'),
            last_updated=current_timestamp + 1
        )
