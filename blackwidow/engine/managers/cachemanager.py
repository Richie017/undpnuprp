import time

from django.conf import settings
from django.core.cache import cache

from blackwidow.engine.decorators.utility import get_models_with_decorator
from config.apps import INSTALLED_APPS
from settings import CACHE_ENABLED

__author__ = 'Tareq'


def log_cache(function):
    def func_wraper(*args, **kwargs):
        if settings.CACHE_ENABLED and settings.LOG_CACHE_TIMING:
            t1 = time.time() * 1000  # converted to millisecond from second
        cached_result = function(*args, **kwargs)

        if settings.CACHE_ENABLED and settings.LOG_CACHE_TIMING:
            t2 = time.time() * 1000  # converted to millisecond from second
            time_taken = t2 - t1
            if time_taken >= settings.MIN_DURATION_CACHE_LOG:
                try:
                    cache_key = args[1]
                except:
                    cache_key = 'N/A'
                cache_log_file = open(settings.CACHE_LOG_FILE_PATH, 'a')
                cache_log_file.write('{},{},{}\n'.format(function.__name__, cache_key, time_taken))
                cache_log_file.close()

        return cached_result

    return func_wraper


class CacheManager(object):
    @classmethod
    @log_cache
    def get_from_cache_by_key(cls, key):
        if CACHE_ENABLED:
            return cache.get(key)
        return None

    @classmethod
    @log_cache
    def set_cache_element_by_key(cls, key, value, timeout=None):
        if CACHE_ENABLED:
            if timeout:
                return cache.set(key, value, timeout)
            return cache.set(key, value)
        return False

    @classmethod
    def clear_entries_in_pattern(cls, pattern, version=None):
        if CACHE_ENABLED:
            cache.delete_pattern(pattern, version=version)

    @classmethod
    def cache_all_reports(cls):
        cachable_reports = get_models_with_decorator('routine_cache', INSTALLED_APPS, include_class=True)

        for r in cachable_reports:
            r.perform_routine_cache()
