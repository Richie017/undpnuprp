"""
Created by tareq on 10/9/17
"""
from django.core.cache import cache

from blackwidow.engine.constants.cache_constants import ONE_WEEK_TIMEOUT
from blackwidow.engine.managers.cachemanager import CacheManager
from config.cache_config import CACHES
import hashlib

__author__ = 'Tareq'


class QuerysetCacheMixin(object):
    @classmethod
    def get_cached_queryset(cls, queryset, key=None):
        if key is None:
            key = hashlib.md5(queryset.query.__str__().encode("utf-8")).hexdigest()

        _queryset = CacheManager.get_from_cache_by_key(key=key)
        if _queryset is None:
            # Cache Miss
            CacheManager.set_cache_element_by_key(key=key, value=queryset, timeout=ONE_WEEK_TIMEOUT)
            _queryset = queryset
        return _queryset
