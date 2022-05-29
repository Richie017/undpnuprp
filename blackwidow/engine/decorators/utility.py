from django.apps import apps

from blackwidow.engine.constants.cache_constants import STATUS_API_PREFIX, ONE_MONTH_TIMEOUT, DELETED_LIST_PREFIX

__author__ = 'mahmudul'


def is_role_context(original_class):
    return original_class


def is_query_context(original_class):
    return original_class


def enable_wizard(original_class):
    return original_class


def save_audit_log(original_class):
    from blackwidow.engine.managers.cachemanager import CacheManager
    from blackwidow.core.models.contracts.base import DomainEntity

    def update_last_updated_time(_class, instance):
        status_key = _class.get_status_api_key()
        decorators = [x.__name__ for x in _class._decorators]
        if 'save_audit_log' in decorators:
            CacheManager.set_cache_element_by_key(STATUS_API_PREFIX + status_key, instance.last_updated,
                                                  ONE_MONTH_TIMEOUT)

        for base in [base_class for base_class in _class.__bases__ if issubclass(base_class, DomainEntity)]:
            update_last_updated_time(base, instance)

    def save(self, *args, **kwargs):
        save._original(self, *args, **kwargs)
        update_last_updated_time(self._meta.model, instance=self)

    save._original = original_class.save
    original_class.save = save

    def update_deleted_cache(_class, instance):
        status_key = _class.get_status_api_key()
        decorators = [x.__name__ for x in _class._decorators]
        if 'save_audit_log' in decorators:
            deleted_list = CacheManager.get_from_cache_by_key(DELETED_LIST_PREFIX + status_key)
            if deleted_list is None:
                deleted_list = list()  # Are we missing the already deleted lists?
            if instance.is_deleted and instance.pk not in deleted_list:
                deleted_list.append(instance.pk)
                CacheManager.set_cache_element_by_key(DELETED_LIST_PREFIX + status_key, deleted_list, ONE_MONTH_TIMEOUT)
            CacheManager.set_cache_element_by_key(STATUS_API_PREFIX + status_key, instance.last_updated,
                                                  ONE_MONTH_TIMEOUT)

        for base in [base_class for base_class in _class.__bases__ if issubclass(base_class, DomainEntity)]:
            update_deleted_cache(base, instance)

    def soft_delete(self, *args, **kwargs):
        soft_delete._original(self, *args, **kwargs)
        update_deleted_cache(self._meta.model, self)

    soft_delete._original = original_class.soft_delete
    original_class.soft_delete = soft_delete

    def update_restored_cache(_class, instance):
        status_key = _class.get_status_api_key()
        decorators = [x.__name__ for x in _class._decorators]
        if 'save_audit_log' in decorators:
            deleted_list = CacheManager.get_from_cache_by_key(DELETED_LIST_PREFIX + status_key)
            if deleted_list is None:
                deleted_list = list()
            if (not instance.is_deleted) and instance.pk in deleted_list:
                deleted_list.remove(instance.pk)
                CacheManager.set_cache_element_by_key(DELETED_LIST_PREFIX + status_key, deleted_list, ONE_MONTH_TIMEOUT)
            CacheManager.set_cache_element_by_key(STATUS_API_PREFIX + status_key, instance.last_updated,
                                                  ONE_MONTH_TIMEOUT)

        for base in [base_class for base_class in _class.__bases__ if issubclass(base_class, DomainEntity)]:
            update_restored_cache(base, instance)

    def restore(self, *args, **kwargs):
        restore._original(self, *args, **kwargs)
        update_restored_cache(self._meta.model, self)

    restore._original = original_class.restore
    original_class.restore = restore

    return original_class


def is_object_context(original_class):
    return original_class


def enable_versioning(*args, **kwargs):
    def enable_versioning(original_class):
        return original_class

    return enable_versioning


def has_status_data(original_class):
    status_data = getattr(original_class, "get_status_data", None)
    if not callable(status_data):
        raise Exception(
            str(original_class) + " is decorated with 'has_status_data' but does not implement 'get_status_data(cls)'")
    return original_class


def direct_delete(original_class):
    return original_class


def routine_cache(original_class):
    cache_data = getattr(original_class, "perform_routine_cache", None)
    if not callable(cache_data):
        raise Exception(
            str(original_class) + " is decorated with 'routine_cache' but does not implement 'perform_routine_cache'")
    return original_class


def loads_initial_data(original_class):
    load_data = getattr(original_class, "load_initial_data", None)
    if not callable(load_data):
        raise Exception(
            str(original_class) + " is decorated with 'loads_initial_data' but does not implement 'load_initial_data'")
    return original_class


def is_queryable(original_class):
    return original_class


def has_data_filter(original_class):
    return original_class


def track_assignments(original_class):
    return original_class


def travarse_child_for_status(original_class):
    return original_class


def decorate(*decorators):
    def register_wrapper(func):
        if '_decorators' not in dir(func):
            func._decorators = tuple()
        for deco in decorators[::-1]:
            func = deco(func)
        func._decorators = decorators
        return func

    return register_wrapper


def get_models_with_decorator_in_app(_app, decorator_name='', app_name=False, include_class=False, **kwargs):
    app = apps.get_app_config(_app)
    m = list()
    for model in app.get_models():
        try:
            if model._decorators is not None:
                for decorator in model._decorators:
                    # print('----- decorate Name : '+decorator.__name__)
                    if decorator.__name__ == decorator_name:
                        if include_class:
                            _m = model
                        else:
                            _m = model.__name__

                        if app_name:
                            m.append((_app, _m))
                        else:
                            m.append(_m)
                        break
        except:
            pass
    return m


def get_models_with_decorator(decorator_name, apps, app_name=False, include_class=False, **kwargs):
    m = list()
    for app in apps:
        try:
            appname = app[app.rfind(".") + 1:]
            # print('+++++++++++++++++ App Name :'+appname)
            m += get_models_with_decorator_in_app(appname, decorator_name, app_name=app_name,
                                                  include_class=include_class, **kwargs)
        except:
            pass
    return m
