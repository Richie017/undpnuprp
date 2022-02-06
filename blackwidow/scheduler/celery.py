from __future__ import absolute_import

import os

from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
# django.setup()

app = Celery('blackwidow.scheduler.trigger_alert')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
    )
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))






    # from __future__ import absolute_import
# import os
# from celery import Celery
# import django
# from django.conf import settings
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
# app = Celery('scheduler.trigger_alert')
# app.config_from_object('django.conf:settings')
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
#
# app.conf.update(
#     CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
#     )
# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))