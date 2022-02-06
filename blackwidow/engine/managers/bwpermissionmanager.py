from blackwidow.core.models.permissions.modulepermission_assignment import ModulePermissionAssignment
from blackwidow.core.models.permissions.rolepermission_assignment import RolePermissionAssignment
from blackwidow.engine.constants.access_permissions import BW_ACCESS_CREATE_MODIFY, BW_ACCESS_MODIFY_ONLY, \
    BW_ACCESS_READ_ONLY, BW_ACCESS_CREATE_MODIFY_DELETE, BW_ACCESS_NO_ACCESS
from blackwidow.engine.constants.cache_constants import PERMISSION_CREATE, ONE_DAY_TIMEOUT, PERMISSION_EDIT, \
    PERMISSION_VIEW, PERMISSION_DELETE, PERMISSION_NO_ACCESS, MODULE_PERMISSION_BY_ROLE, ACCESS_PERMISSION_BY_ROLE
from blackwidow.engine.managers.cachemanager import CacheManager

__author__ = 'ActiveHigh'


class BWPermissionManager(object):
    @staticmethod
    def __has_permission(request, model, permission, *args, **kwargs):
        all_objects = BWPermissionManager.get_access_permissions_by_role(role=request.c_user.role)

        # checking permission of virtually created models(proxy model) for this role
        _proxy_model_name = kwargs.get('proxy_model_name', None)
        if _proxy_model_name is not None:
            if request.user is not None:
                return any(
                    filter(lambda x: x.permission.context == _proxy_model_name and x.access >= int(permission['value']),
                           all_objects))
            return False

        if model is None or all(map(lambda x: x.__name__ != 'is_object_context', model._decorators)):
            return True

        for decorator in model._decorators:
            if decorator.__name__ == "is_object_context":
                if request.user is not None:
                    return any(filter(
                        lambda x: x.permission.context == model.__name__ and x.access >= int(permission['value']),
                        all_objects))
                return False

        _module = model.get_model_meta('route', 'module')
        _sub_modules = model.get_model_meta('route', 'group')

        all_modules = BWPermissionManager.get_module_permissions_by_role(role=request.c_user.role)
        if any(filter(lambda x: x.module.name == _module.value['title'], all_modules)):
            module = list(filter(lambda x: x.module.name == _module.value['title'], all_modules))[0]
            if module.access < int(permission['value']):
                return False
            if isinstance(_sub_modules, (list, tuple)):
                for _s in _sub_modules:
                    if any(filter(lambda
                                          x: x.module.name == _s and x.module.parent is not None and x.module.parent.id == module.module.id and x.access < int(
                        permission['value']), all_modules)):
                        return False
            else:
                if any(filter(lambda
                                      x: x.module.name == _sub_modules and x.module.parent is not None and x.module.parent.id == module.module.id and x.access < int(
                    permission['value']), all_modules)):
                    return False
            return True
        return False

    @staticmethod
    def has_create_permission(request, model, *args, **kwargs):
        permission_key = PERMISSION_CREATE + model.__name__ + '_' + str(request.c_user.role_id)
        cached_permission = CacheManager.get_from_cache_by_key(permission_key)
        if cached_permission is None:
            cached_permission = BWPermissionManager.__has_permission(request, model, BW_ACCESS_CREATE_MODIFY, *args,
                                                                     **kwargs)
            CacheManager.set_cache_element_by_key(permission_key, cached_permission, ONE_DAY_TIMEOUT)
        return cached_permission

    @staticmethod
    def has_edit_permission(request, model, *args, **kwargs):
        permission_key = PERMISSION_EDIT + model.__name__ + '_' + str(request.c_user.role_id)
        cached_permission = CacheManager.get_from_cache_by_key(permission_key)
        if cached_permission is None:
            cached_permission = BWPermissionManager.__has_permission(request, model, BW_ACCESS_MODIFY_ONLY, *args,
                                                                     **kwargs)
            CacheManager.set_cache_element_by_key(permission_key, cached_permission, ONE_DAY_TIMEOUT)
        return cached_permission

    @staticmethod
    def has_view_permission(request, model, *args, **kwargs):
        permission_key = PERMISSION_VIEW + model.__name__ + '_' + str(request.c_user.role_id)
        cached_permission = CacheManager.get_from_cache_by_key(permission_key)
        if cached_permission is None:
            cached_permission = BWPermissionManager.__has_permission(request, model, BW_ACCESS_READ_ONLY, *args,
                                                                     **kwargs)
            CacheManager.set_cache_element_by_key(permission_key, cached_permission, ONE_DAY_TIMEOUT)
        return cached_permission

    @staticmethod
    def has_delete_permission(request, model, *args, **kwargs):
        permission_key = PERMISSION_DELETE + model.__name__ + '_' + str(request.c_user.role_id)
        cached_permission = CacheManager.get_from_cache_by_key(permission_key)
        if cached_permission is None:
            cached_permission = BWPermissionManager.__has_permission(request, model, BW_ACCESS_CREATE_MODIFY_DELETE,
                                                                     *args, **kwargs)
            CacheManager.set_cache_element_by_key(permission_key, cached_permission, ONE_DAY_TIMEOUT)
        return cached_permission

    @staticmethod
    def has_no_permission(request, model, *args, **kwargs):
        permission_key = PERMISSION_NO_ACCESS + model.__name__ + '_' + str(request.c_user.role_id)
        cached_permission = CacheManager.get_from_cache_by_key(permission_key)
        if cached_permission is None:
            cached_permission = BWPermissionManager.__has_permission(request, model, BW_ACCESS_NO_ACCESS, *args,
                                                                     **kwargs)
            CacheManager.set_cache_element_by_key(permission_key, cached_permission, ONE_DAY_TIMEOUT)
        return cached_permission

    @staticmethod
    def get_module_permissions_by_role(role, database_name='default', overwrite=False):
        """
        Get cached list of module permission assignments of the role
        :param role: role object
        :param database_name: target database to read from
        :param overwrite: If True, then cache will be re-written from DB, even if there is existing entry in cache
        :return: cached list of module permission assignments of the role
        """
        permission_key = MODULE_PERMISSION_BY_ROLE + str(role.id)
        cached_permission = CacheManager.get_from_cache_by_key(permission_key)
        if cached_permission is None or overwrite:
            cached_permission = list(
                ModulePermissionAssignment.objects.using(database_name).prefetch_related('module',
                                                                                         'module__parent').filter(
                    role=role))
            CacheManager.set_cache_element_by_key(permission_key, cached_permission, ONE_DAY_TIMEOUT)
        return cached_permission

    @staticmethod
    def get_access_permissions_by_role(role, database_name='default', overwrite=False):
        """
        Get cached list of role permission assignments of the role
        :param role: role object
        :param database_name: target database to read from
        :param overwrite: If True, then cache will be re-written from DB, even if there is existing entry in cache
        :return: cached list of role permission assignments of the role
        """
        permission_key = ACCESS_PERMISSION_BY_ROLE + str(role.id)
        cached_permission = CacheManager.get_from_cache_by_key(permission_key)
        if cached_permission is None or overwrite:
            cached_permission = list(
                RolePermissionAssignment.objects.using(database_name).prefetch_related('permission').filter(
                    role=role))
            CacheManager.set_cache_element_by_key(permission_key, cached_permission, ONE_DAY_TIMEOUT)
        return cached_permission
