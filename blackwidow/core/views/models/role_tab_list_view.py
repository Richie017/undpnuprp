from datetime import datetime

from django.conf import settings
from django.db import transaction
from django.db.models.query_utils import Q

from blackwidow.core.generics.views.partial_views.partial_tab_list_view import PartialGenericTabListView
from blackwidow.core.models.permissions.modulepermission_assignment import ModulePermissionAssignment
from blackwidow.core.models.permissions.rolepermission_assignment import RolePermissionAssignment
from blackwidow.core.models.roles.role import Role
from blackwidow.core.views.menu.menu_renderer_view import MenuRendererView
from blackwidow.engine.constants.access_permissions import BW_ACCESS_CREATE_MODIFY, BW_ACCESS_MODIFY_ONLY, \
    BW_ACCESS_READ_ONLY, BW_ACCESS_CREATE_MODIFY_DELETE, BW_ACCESS_NO_ACCESS
from blackwidow.engine.constants.cache_constants import PERMISSION_CREATE, PERMISSION_EDIT, \
    PERMISSION_VIEW, PERMISSION_DELETE, PERMISSION_NO_ACCESS, ONE_MONTH_TIMEOUT, MODULE_PERMISSION_TIME_CACHE, \
    ROLE_PERMISSION_TIME_CACHE
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.exceptions.exceptions import NotEnoughPermissionException
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager
from blackwidow.engine.managers.cachemanager import CacheManager
from blackwidow.engine.routers.database_router import BWDatabaseRouter

__author__ = 'Mahmud'


@decorate(override_view(model=Role, view=ViewActionEnum.Tab))
class PartialRoleTabListView(PartialGenericTabListView):
    def choose_database(self, request, **kwargs):
        return BWDatabaseRouter.get_write_database_name()

    def get(self, request, *args, **kwargs):
        return super(PartialRoleTabListView, self).get(request, *args, **kwargs)

    def post(self, request, *args, pk=0, **kwargs):
        if not BWPermissionManager.has_edit_permission(self.request, self.model, *args, **kwargs):
            raise NotEnoughPermissionException("You do not have enough permission to do this action.")

        model = self.model.objects.filter(id=int(pk))[0]
        tab = [x for x in model.tabs_config if x.access_key == kwargs['tab']][0]
        for key in request.POST:
            with transaction.atomic():
                if key.__contains__(model.name):
                    permission_context = key.split('__')[0]
                    landing_model_id = request.POST.get(key, '')
                    if tab.access_key == "top_menus":
                        items = tab.get_queryset().filter(
                            module__name=permission_context)
                        for item in items:
                            if landing_model_id != '':
                                item.landing_model_id = int(landing_model_id)
                                item.save()
                            else:
                                item.landing_model = None
                                item.save()
                        continue
                if tab.access_key == "top_menus":
                    items = tab.get_queryset().filter(
                        module__name=key)
                elif tab.access_key == "modules":
                    items = tab.get_queryset().filter(
                        module__name=key)
                elif tab.access_key == "permissions":
                    items = tab.get_queryset().filter(
                        permission__context=key)
                if items.exists():
                    item = items.first()
                    values = request.POST.get(key, None)
                    if values is not None:
                        _v = max([int(v) for v in values.split(',')])
                        if item.access == _v:
                            continue
                        item.access = _v
                        item.save()
                        self.update_permission_for_role(role=model, model=key, access=_v)

                        if tab.access_key == "top_menus":
                            self.sub_module_permission_update(role=model, parent_module_permission=item, access=_v)
                        elif tab.access_key == "modules":
                            self.object_permission_update(role=model, module_permission=item, access=_v)

        # update js menu config of the role if JS_MENU_RENDERING is enabled
        if hasattr(settings, 'ENABLE_JS_MENU_RENDERING') and settings.ENABLE_JS_MENU_RENDERING:
            MenuRendererView.save_role_menu_config(role=model)
        return self.get(request, *args, pk=pk, **kwargs)

    def sub_module_permission_update(self, role=None, parent_module_permission=None, access=0):
        if role is not None and parent_module_permission is not None:
            sub_module_permissions = ModulePermissionAssignment.objects.filter(
                Q(role__id=role.id) & Q(module__parent__name=parent_module_permission.module.name))
            if len(sub_module_permissions) < 1:
                self.object_permission_update(role=role, module_permission=parent_module_permission, access=access)
                return
            for sub_module_permission in sub_module_permissions:
                if sub_module_permission.access == access:
                    continue
                sub_module_permission.access = access
                sub_module_permission.save()
                self.object_permission_update(role=role, module_permission=sub_module_permission, access=access)

    def object_permission_update(self, role=None, module_permission=None, access=0):
        object_permissions = RolePermissionAssignment.objects.filter(Q(role__id=role.id)).filter(
            permission__group_id=module_permission.module_id)
        for object_permission in object_permissions:
            try:
                permission_context = object_permission.permission.context
                object_permission.access = access
                object_permission.save()
                self.update_permission_for_role(role=role, model=permission_context, access=access)
            except:
                continue

    @classmethod
    def update_permission_for_role(cls, role, model, access):
        cache_key_suffix = str(model) + '_' + str(role.id)
        current_timestamp = datetime.now().timestamp() * 1000

        # Set permissions based on the value of access.
        CacheManager.set_cache_element_by_key(key=PERMISSION_NO_ACCESS + cache_key_suffix,  # No access permission
                                              value=(access == int(BW_ACCESS_NO_ACCESS['value'])),  # True or False
                                              timeout=ONE_MONTH_TIMEOUT)
        CacheManager.set_cache_element_by_key(key=PERMISSION_VIEW + cache_key_suffix,  # View permission
                                              value=(access >= int(BW_ACCESS_READ_ONLY['value'])),  # True or False
                                              timeout=ONE_MONTH_TIMEOUT)
        CacheManager.set_cache_element_by_key(key=PERMISSION_EDIT + cache_key_suffix,  # Edit permission
                                              value=(access >= int(BW_ACCESS_MODIFY_ONLY['value'])),  # True or False
                                              timeout=ONE_MONTH_TIMEOUT)
        CacheManager.set_cache_element_by_key(key=PERMISSION_CREATE + cache_key_suffix,  # Create permission
                                              value=(access >= int(BW_ACCESS_CREATE_MODIFY['value'])),  # True or False
                                              timeout=ONE_MONTH_TIMEOUT)
        CacheManager.set_cache_element_by_key(key=PERMISSION_DELETE + cache_key_suffix,  # Delete permission
                                              value=(access >= int(BW_ACCESS_CREATE_MODIFY_DELETE['value'])),
                                              timeout=ONE_MONTH_TIMEOUT)
        CacheManager.set_cache_element_by_key(key=MODULE_PERMISSION_TIME_CACHE, value=current_timestamp,
                                              timeout=ONE_MONTH_TIMEOUT)
        CacheManager.set_cache_element_by_key(key=ROLE_PERMISSION_TIME_CACHE, value=current_timestamp,
                                              timeout=ONE_MONTH_TIMEOUT)
