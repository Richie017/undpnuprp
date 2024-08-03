from blackwidow.core.models.common.settings_item import SettingsItem
from blackwidow.engine.constants.cache_constants import USER_TIMEZONE_CACHE, ONE_MONTH_TIMEOUT
from blackwidow.engine.managers.cachemanager import CacheManager
from settings import TIME_ZONE_DEFAULT_OFFSET

__author__ = 'Tareq'


class TimeZoneSettingsItem(SettingsItem):
    def format_value(self, value):
        v = (-1) * int(value) / 60
        return "GMT " + ('' if v == 0 else ('+' if v > 0 else '-')) + ' ' + str(v)

    class Meta:
        proxy = True

    @classmethod
    def cache_user_timezone_offset(cls, user_id, offset_value=None):
        if offset_value is None:
            offset_value = TIME_ZONE_DEFAULT_OFFSET
        key = USER_TIMEZONE_CACHE + str(user_id)
        CacheManager.set_cache_element_by_key(key=key, value=offset_value, timeout=ONE_MONTH_TIMEOUT)

    @classmethod
    def get_cached_user_timezone_offset(cls, user):
        key = USER_TIMEZONE_CACHE + str(user.pk)
        cached_value = CacheManager.get_from_cache_by_key(key=key)
        if cached_value is None:
            # timezone_setting = TimeZoneSettingsItem.objects.filter(organization_id=user.organization_id).first()
            # if timezone_setting is None
            # cached_value = user.settings_value.get(settings_item=timezone_setting).value
            cached_value = TIME_ZONE_DEFAULT_OFFSET
            CacheManager.set_cache_element_by_key(key=key, value=cached_value, timeout=ONE_MONTH_TIMEOUT)
        return cached_value
