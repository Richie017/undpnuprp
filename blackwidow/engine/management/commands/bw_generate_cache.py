from django.core.management.base import BaseCommand

from blackwidow.engine.decorators.utility import get_models_with_decorator
from settings import INSTALLED_APPS

__author__ = 'Tareq'


class Command(BaseCommand):
    def handle(self, *args, **options):
        cachable_reports = get_models_with_decorator('routine_cache', INSTALLED_APPS, include_class=True)

        for r in cachable_reports:
            r.perform_routine_cache()
