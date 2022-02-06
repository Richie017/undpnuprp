from django.core.management.base import BaseCommand

from blackwidow.core.generics.views.import_view import get_model
from blackwidow.engine.decorators.utility import get_models_with_decorator
from settings import INSTALLED_APPS

__author__ = 'Tareq'


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('model', nargs='+', type=str)

    def handle(self, *args, **options):
        if options['model'] is None or len(options['model']) == 0 or 'all' in options['model']:
            cachable_reports = get_models_with_decorator('routine_cache', INSTALLED_APPS, include_class=True)

            for r in cachable_reports:
                try:
                    cache_model = get_model(app_label='reports', model_name=r.__name__ + 'Cache')
                    print("Model: %s, existing member: %d" % (cache_model.__name__, cache_model.objects.count()))
                    cache_model.objects.all().delete()
                except:
                    print("No cache found for model: %s" % r.__name__)
        else:
            for model_name in options['model']:
                if not model_name.endswith('Cache'):
                    model_name = model_name + 'Cache'
                try:
                    cache_model = get_model(app_label='reports', model_name=model_name)
                    print("Model: %s, existing member: %d" % (cache_model.__name__, cache_model.objects.count()))
                    cache_model.objects.all().delete()
                except:
                    print("No cache model found: %s" % model_name)
