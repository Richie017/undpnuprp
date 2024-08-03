import json
from datetime import datetime
from threading import Thread

from django.conf import settings

from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.core.models import Role, RolePermissionAssignment
from blackwidow.core.models.menumanager.menu_manager import MenuManager
from blackwidow.core.models.modules.module import BWModule
from blackwidow.core.models.permissions.rolepermission import RolePermission
from blackwidow.core.views import MenuRendererView
from blackwidow.engine.constants.cache_constants import ROLE_PERMISSION_TIME_CACHE, ONE_MONTH_TIMEOUT
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.managers.cachemanager import CacheManager

__author__ = 'Shamil, Ziaul Haque'


@decorate(override_view(model=MenuManager, view=ViewActionEnum.Manage))
class MenuManagerView(GenericListView):
    def get_template_names(self):
        return ['common/menu_manager/_list.html']

    def post(self, request, *args, **kwargs):
        try:
            data = request.POST.get('menu_data', None)
            if data:
                data = json.loads(data)
                if len(data) > 0:
                    for top_menu in data[0]:
                        top_menu_id = top_menu['id']
                        if len(top_menu['children']) > 0:
                            for sm_index, side_module in enumerate(top_menu['children'][0], 1):
                                side_module_name = side_module['name']
                                s_module = BWModule.objects.get(pk=side_module['id'])
                                s_module.parent_id = top_menu_id
                                s_module.name = side_module_name
                                s_module.module_order = sm_index
                                s_module.save()
                                if len(side_module['children']) > 0:
                                    for mi_index, menu_item in enumerate(side_module['children'][0], 1):
                                        menu_item_name = menu_item['name']
                                        m_item = RolePermission.objects.get(pk=menu_item['id'])
                                        m_item.item_order = mi_index
                                        m_item.group_name = side_module_name
                                        m_item.display_name = menu_item_name
                                        m_item.save()

                    # generate js menu config for all roles
                    Thread(target=self.generate_js_menu_config).start()
        except Exception as exp:
            pass
        return super(MenuManagerView, self).get(request, *args, **kwargs)

    @classmethod
    def generate_js_menu_config(cls):
        # generate js menu config for all roles only when ENABLE_JS_MENU_RENDERING is true
        if hasattr(settings, 'ENABLE_JS_MENU_RENDERING') and settings.ENABLE_JS_MENU_RENDERING:
            for _role in Role.objects.all():
                MenuRendererView.save_role_menu_config(role=_role)

            # update latest RolePermissionAssignment object's last_updated field by current timestamp
            current_timestamp = datetime.now().timestamp() * 1000
            permission_pk = RolePermissionAssignment.objects.order_by('-last_updated').first().pk
            RolePermissionAssignment.objects.filter(pk=permission_pk).update(last_updated=current_timestamp)
            print('---> Print..........')
            # set cache for role permission time
            CacheManager.set_cache_element_by_key(
                key=ROLE_PERMISSION_TIME_CACHE,
                value=current_timestamp,
                timeout=ONE_MONTH_TIMEOUT
            )

    def get_context_data(self, **kwargs):
        context_data = super(MenuManagerView, self).get_context_data(**kwargs)
        modules = BWModule.objects.all()
        context_data['top_modules'] = modules.filter(parent__isnull=True).order_by('module_order')
        context_data['side_modules'] = modules.filter(parent__isnull=False)
        context_data['side_menu_items'] = RolePermission.objects.filter(hide=False)
        return context_data
