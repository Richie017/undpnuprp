"""
    Written by tareq on 8/9/18
"""
from threading import Thread

from celery.app.task import Task
from django.conf import settings

__author__ = 'Tareq'


def perform_async(method, args=(), kwargs={}, delay=2):
    """
    perform_async method is used to call a method asynchronously. If the method is a celery task, it is called using
    celery's "delay" method. If not, then a thread is spawned to call the method.
    :param method: a callable
    :param args: positional arguments for the method
    :param kwargs: keyword arguments for the method
    :param delay: time to wait before task in seconds
    :return: None
    """

    # Check if the method is celery task
    if isinstance(method, Task) and settings.CELERY_ENABLED:
        method.apply_async(
            args=args, kwargs=kwargs, countdown=delay)  # task will start at least after 2 second of the response

    else:
        # if the method is not a celery task, a thread is spawned
        thread = Thread(target=method, args=args, kwargs=kwargs)
        thread.start()
