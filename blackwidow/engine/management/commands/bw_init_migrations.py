import inspect

__author__ = 'mahmudul'

from settings import *

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.requires_model_validation = False

    def pred(self, c):
        return inspect.isclass(c) and c.__module__ == self.pred.__module__

    def handle(self, *args, **options):
        from config.apps import INSTALLED_APPS
        for x in INSTALLED_APPS:
            v = os.path.join(x.replace('.', os.sep), 'migrations')
            if not os.path.isdir(v) and not os.path.exists(v):
                self.stdout.write('Creating migration folder for ....' + v)
                os.makedirs(v)
            open(os.path.join(v, '__init__.py'), 'w').close()
        self.stdout.write('Migrations folders added.')
