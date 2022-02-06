import copy
import json
import os

from django import http
from django.conf import settings
from django.db.models.query_utils import Q
from django.template import Context, Engine
from django.views.generic.base import View

from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.models.modules.module import BWModule
from blackwidow.core.models.permissions.modulepermission_assignment import ModulePermissionAssignment
from blackwidow.core.models.permissions.rolepermission import RolePermission
from blackwidow.engine.constants.access_permissions import BW_ACCESS_READ_ONLY
from blackwidow.engine.extensions.menu_extensions import role_filify
from blackwidow.engine.file_handlers.aws_file_writer import AWSFileWriter
from config.aws_s3_config import AWS_LOCATION
from config.model_json_cache import MENU_JSON_DIR_SUFFIX

MODEL_JASON_DIR = settings.MODEL_JASON_DIR
MENU_JASON_FILE_SUFFIX = settings.MENU_JASON_FILE_SUFFIX
MODULE_TITLES = settings.MODULE_TITLES
MODULE_URLS = settings.MODULE_URLS
S3_STATIC_ENABLED = getattr(settings, 'S3_STATIC_ENABLED', False)

__author__ = "Shamil, Ziaul Haque"


class MenuRendererView(View):

    @classmethod
    def get_top_module_url(cls, module_permissions=None, module=None, language_code='', **kwargs):
        module_url = module_permissions.get(module__name=module.name)['landing_model__route_name']
        if module_url is None:
            _module_url = MODULE_URLS.get(module.module_url, None)
            if _module_url:
                return '/' + language_code + _module_url + '/'
            return '/' + language_code + module.module_url + '/dashboard'
        return '/' + language_code + module_url + '/'

    @classmethod
    def get_top_module_order(cls, module=None, **kwargs):
        order = None
        if hasattr(settings, 'MODULE_ORDERS'):
            order = settings.MODULE_ORDERS.get(module.module_url, None)
        if order is None:
            return module.module_order
        return order

    @classmethod
    def get_top_module_icon(cls, module=None, **kwargs):
        icon = None
        if hasattr(settings, 'MODULE_ICONS'):
            icon = settings.MODULE_ICONS.get(module.module_url, None)
        if icon is None:
            return module.icon
        return icon

    @classmethod
    def filter_role_menu(cls, default_menu):
        filtered_menu = []
        for menu in default_menu:
            if len(menu['items']) > 0:
                filtered_menu.append(menu)
        return filtered_menu

    @classmethod
    def resolve_role_menu_urls(cls, menuitems):
        cached = copy.deepcopy(menuitems)
        n_items = []
        for item in cached:
            if len(item.get('items', [])) > 0:
                item['items'] = cls.resolve_role_menu_urls(item['items'])
            else:
                item['items'] = []
            n_items += (item,)
            if len(item['items']) == 0 and item['link'] == '' and item in n_items:
                n_items.remove(item)
        return n_items

    @classmethod
    def save_role_menu_config(cls, role=None, *args, **kwargs):
        if role is None:
            return ''
        role_short_name = role_filify(role.name)
        js_file_name = role_short_name
        print(role_short_name)
        role_id = role.pk
        menu_config = []
        url_mapping = {}
        all_modules = BWModule.objects.filter(
            (Q(parent__isnull=True) | Q(parent__parent__isnull=True)) &
            Q(role=role_id, modulepermissionassignment__access__gte=1)
        ).distinct()

        top_modules = all_modules.filter(parent__isnull=True).order_by('module_order')
        top_module_permissions = ModulePermissionAssignment.objects.filter(
            role_id=role_id, module__name__in=[m.name for m in top_modules]
        ).values('module__name', 'landing_model__route_name')
        menu_groups = all_modules.filter(parent__isnull=False).order_by('module_order')
        menu_items = RolePermission.objects.filter(
            Q(hide=False, role=role_id, permission__access__gte=1)
        ).order_by('item_order')
        for module in top_modules:
            p_module = dict()
            p_module['title'] = MODULE_TITLES.get(module.name, module.name)
            p_module['link'] = cls.get_top_module_url(
                module_permissions=top_module_permissions, module=module
            )
            p_module['order'] = cls.get_top_module_order(module=module)
            p_module['icon'] = cls.get_top_module_icon(module=module)
            p_module['items'] = []
            m_groups = menu_groups.filter(
                parent_id=module.pk
            ).order_by('module_order')
            for group in m_groups:
                m_group = dict()
                m_group['title'] = group.name
                m_group['link'] = group.module_url
                m_group['order'] = group.module_order
                m_group['items'] = []
                m_items = menu_items.filter(
                    group_id=group.pk
                ).order_by('item_order')
                for item in m_items:
                    m_item = dict()
                    m_item['title'] = item.display_name
                    m_item['link'] = '/' + item.route_name + '/'
                    m_item['order'] = item.item_order
                    m_item['hide'] = item.hide
                    m_item['required-permission'] = list()
                    m_item['required-permission'].append(dict(
                        app=item.app_label,
                        context=item.context,
                        access=int(BW_ACCESS_READ_ONLY['value'])
                    ))
                    m_group['items'].append(m_item)
                    url_mapping[m_item['link']] = p_module['title']
                p_module['items'].append(m_group)
            menu_config.append(p_module)
        menu_config = cls.resolve_role_menu_urls(menu_config)
        menu_config = cls.filter_role_menu(menu_config)
        template = Engine().from_string(role_permission_jason_template)
        indent = lambda s: s.replace('\n', '\n  ')
        context = Context({
            'menu_config': indent(json.dumps(menu_config, sort_keys=True, indent=4)),
            'url_mapping': indent(json.dumps(url_mapping, sort_keys=True, indent=4))
        })
        script = http.HttpResponse(template.render(context), 'text/javascript')
        try:
            # If using s3 as static file server, need to write the JS file in s3 bucket
            if S3_STATIC_ENABLED:
                file_dir = AWS_LOCATION + MENU_JSON_DIR_SUFFIX + 'roles/'
                file_name = file_dir + js_file_name + MENU_JASON_FILE_SUFFIX
                file_content = script.content.decode("utf-8")
                AWSFileWriter.upload_file_with_content(file_name=file_name, content=file_content)
            else:
                _dir_suffix = MODEL_JASON_DIR + 'roles/'
                os.makedirs(_dir_suffix, exist_ok=True)
                with open(_dir_suffix + js_file_name + MENU_JASON_FILE_SUFFIX, 'w') as f:
                    f.write(script.content.decode("utf-8"))
        except Exception as exp:
            ErrorLog.log(exp=exp)
        return script

    def get(self, request, *args, **kwargs):
        return self.save_role_menu_config(role=request.user.consoleuser.role)


role_permission_jason_template = r"""
{% autoescape off %}
var menu_config = {{ menu_config }};
var url_mapping = {{ url_mapping }};
{% endautoescape %}
"""
