from blackwidow.core.models import ApiCallLog
from blackwidow.engine.constants.cache_constants import LOG_CACHE_PREFIX, ONE_MONTH_TIMEOUT
from blackwidow.engine.managers.cachemanager import CacheManager

__author__ = 'Tareq'


class LogCacheManager(object):
    @classmethod
    def get_cacheable_log_models(cls):
        return [ApiCallLog]

    @classmethod
    def write_logs_to_database(cls):
        log_models = cls.get_cacheable_log_models()

        for model in log_models:
            log_cache_key = LOG_CACHE_PREFIX + model.__name__
            log_cache_dict = CacheManager.get_from_cache_by_key(key=log_cache_key)
            CacheManager.clear_entries_in_pattern(pattern=log_cache_key)
            CacheManager.set_cache_element_by_key(key=log_cache_key, value={}, timeout=ONE_MONTH_TIMEOUT)

            if log_cache_dict:
                for key, obj in log_cache_dict.items():
                    try:
                        obj.save()
                    except Exception as exp:
                        print(exp)
