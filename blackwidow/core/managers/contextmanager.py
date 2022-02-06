import copy

from django.apps import apps
from django.conf import settings
from django.contrib.auth import login
from django.core.urlresolvers import reverse, NoReverseMatch

from blackwidow.core.models.common.sessionkey import SessionKey
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.core.models.users.settings.user_settings import TimeZoneSettingsItem
from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager
from blackwidow.engine.managers.menumanager import MenuManager
from blackwidow.engine.routers.database_router import BWDatabaseRouter

get_model = apps.get_model

__author__ = 'mahmudul'


class ContextManager(object):
    @classmethod
    def has_authkey(cls, request):
        if request.GET.get('authkey', None) is not None:
            return True
        if request.POST.get('authkey', None) is not None:
            return True
        return False

    @classmethod
    def get_authkey(cls, request):
        if request.GET.get('authkey', None) is not None:
            return request.GET.get('authkey', None)
        if request.POST.get('authkey', None) is not None:
            return request.POST.get('authkey', None)
        return None

    @classmethod
    def get_access_permissions(cls, user, request=None):
        return BWPermissionManager.get_access_permissions_by_role(user.role)

    @classmethod
    def get_module_permissions(cls, user, request=None):
        return BWPermissionManager.get_module_permissions_by_role(user.role)

    @classmethod
    def get_current_organization(cls, request):
        context = cls.get_current_context(request)
        if context is None:
            raise Exception('Context not found')
        if context['organization'] is None:
            raise Exception('Organization is not set for this context')
        return context['organization']

    @classmethod
    def get_current_user(cls, request):
        context = cls.get_current_context(request)
        if context is None:
            raise Exception('Context not found')
        if context['user'] is None:
            raise Exception('User is not set for this context')
        return context['user']

    @classmethod
    def apply_notifications(cls, context, c_user=None, c_organization=None):
        return context

    @classmethod
    def filter_menu(cls, default_menu):
        filtered_menu = []
        for menu in default_menu:
            if len(menu['items']) > 0:
                filtered_menu.append(menu)
        return filtered_menu

    @classmethod
    def initialize_context(cls, request, kwargs):
        context = None
        request.c_request_path = '/' + request.path_info.split('/', 2)[-1]
        user = kwargs.get('user')
        org = kwargs.get('org')
        device = kwargs.get('device')
        if org is not None:
            menu = cls.resolve_menu_urls(request,
                                         list(cls.get_module_permissions(user=user)),
                                         list(cls.get_access_permissions(user=user)),
                                         cls.get_menu_items())
            menu = cls.filter_menu(menu)
            context = {
                'organization': org.to_json(),
                'user': user.to_json(),
                'menu': menu,
                'module_titles': settings.MODULE_TITLES,
                'breadcrumb': cls.build_breadcrumb(menu),
                'context_list': []
            }

        cls.apply_notifications(context)

        if not cls.has_authkey(request):
            request.session['context'] = context
        else:
            _u = user.user
            _u.backend = cls.get_authkey(request)
            login(request, _u)
        request.user = user.user
        request.c_user = user
        request.c_organization = org if org is not None else user.organization
        request.c_device = device
        try:
            request.c_tz_offset = TimeZoneSettingsItem.get_cached_user_timezone_offset(user=request.c_user)
        except Exception as exp:
            request.c_tz_offset = 0
        return request

    @classmethod
    def get_current_context(cls, request):
        if cls.has_authkey(request):
            # authkey = ContextManager.get_authkey(request)
            # sess_key = SessionKey.objects.using(BWDatabaseRouter.get_read_database_name()).filter(ses_key=authkey)[0]
            c_user = request.c_user
            menu = cls.resolve_menu_urls(request,
                                         list(cls.get_module_permissions(user=c_user)),
                                         list(cls.get_access_permissions(user=c_user)),
                                         cls.get_menu_items())
            menu = cls.filter_menu(menu)
            context = {
                'organization': c_user.organization.to_json(),
                'user': c_user.to_json(),
                'menu': menu,
                'module_titles': settings.MODULE_TITLES,
                'breadcrumb': cls.build_breadcrumb(menu),
                'context_list': [x.to_json() for x in Organization.objects.filter().exclude(id=c_user.organization.id)]
            }
            cls.apply_notifications(context)
            return context

        return request.session.get('context', None)

    # kwargs must have at least org & user / context defined
    @classmethod
    def set_current_context(cls, request, kwargs):
        user = kwargs.get('user')
        org = kwargs.get('org')
        if kwargs.get('context') is not None:
            # verify context
            context = kwargs.get('context')
            orgs = Organization.objects.filter(id=context['organization']['id'])
            if len(orgs) > 0:
                org = orgs[0]

            users = ConsoleUser.objects.filter(id=context['user']['id'])
            if len(users) > 0:
                user = users[0]

            if org is None:
                raise Exception('Organization not found')
            if user is None:
                raise Exception('Organization not found')
            request.session['context'] = context

        elif org is not None:
            if org is None:
                raise Exception('Organization not found')

        if user is None:
            if org is None and user is None:
                raise Exception('User not found')

        # both org and user is found. therefore switch context
        menu = ContextManager.resolve_menu_urls(request,
                                                list(cls.get_module_permissions(user=user)),
                                                list(cls.get_access_permissions(user=user)),
                                                cls.get_menu_items())
        menu = cls.filter_menu(menu)
        context = {
            'organization': org.to_json(),
            'user': user.to_json(),
            'menu': menu,
            'module_titles': settings.MODULE_TITLES,
            'breadcrumb': cls.build_breadcrumb(menu),
            'context_list': [x.to_json() for x in Organization.objects.filter().exclude(id=org.id)]
        }
        user.current_org = org.id
        user.save(request=request, context=cls.get_current_context(request))

        cls.apply_notifications(context)
        if not ContextManager.has_authkey(request):
            request.session['context'] = context
        else:
            _u = user.user
            _u.backend = cls.get_authkey(request)
            login(request, _u)
        request.c_user = user
        request.c_organization = user.organization
        try:
            request.c_tz_offset = TimeZoneSettingsItem.get_cached_user_timezone_offset(user=request.c_user)
        except Exception as exp:
            request.c_tz_offset = 0
        return request

    @classmethod
    def __has_permission(cls, model, access, permissions):
        if model is None:
            return True
        # TODO Handle Role Permission check for Proxy Lebeled Menu Items
        for decorator in model._decorators:
            if decorator.__name__ == "is_object_context":
                return any(filter(lambda x: x.permission.context == model.__name__ and x.access >= access, permissions))
        return True

    @classmethod
    def __has_module_access(cls, model, access, modules):
        if model is None:
            return True
        # TODO Handle Module Permission check for Proxy Lebeled Menu Items

        _module = model.get_model_meta('route', 'module')
        _sub_modules = model.get_model_meta('route', 'group')

        if any(filter(lambda x: x.module.name == _module.value['title'], modules)):
            module = list(filter(lambda x: x.module.name == _module.value['title'], modules))[0]
            if module.access < access:
                return False
            if isinstance(_sub_modules, (list, tuple)):
                for _s in _sub_modules:
                    if any(filter(lambda x: x.module.name == _s and x.module.parent is not None and x.module.parent.id == module.module.id and x.access < access, modules)):
                        return False
            else:
                if any(filter(lambda x: x.module.name == _sub_modules and x.module.parent is not None and x.module.parent.id == module.module.id and x.access < access, modules)):
                    return False
            return True
        return False

    @classmethod
    def is_menu_visible(cls, modules, permissions, menuitem):
        if 'required-permission' in menuitem:
            perm_result = True
            module_result = True
            for r in menuitem['required-permission']:
                try:
                    model = get_model(r['app'], r['context'])
                    perm_result &= cls.__has_permission(model, r['access'], permissions)
                except LookupError:
                    perm_result &= cls.__has_permission(None, r['access'], permissions)

            for r in menuitem['required-permission']:
                try:
                    model = get_model(r['app'], r['context'])
                    module_result &= cls.__has_module_access(model, r['access'], modules)
                except LookupError:
                    perm_result &= cls.__has_module_access(None, r['access'], modules)

            return perm_result and module_result
        return True

    @classmethod
    def build_breadcrumb(cls, menuitems):
        items = []
        for i in menuitems:
            if i['active'] == 'active' or i['open'] == 'open':
                if i['link'] != '':
                    new_item = {
                        'url': i['link'],
                        'name': i['title']
                    }
                    items.append(new_item)
                items += cls.build_breadcrumb(i['items'])
        return items

    @classmethod
    def get_menu_items(cls):
        # checking JS_MENU_RENDERING is enabled or not, if enabled then return empty list else call generate_menu_dict()
        if hasattr(settings, 'ENABLE_JS_MENU_RENDERING') and settings.ENABLE_JS_MENU_RENDERING:
            return []
        return MenuManager.generate_menu_dict()

    @classmethod
    def resolve_menu_urls(cls, request, modules, permissions, menuitems):
        cached = copy.deepcopy(menuitems)
        n_items = []
        for item in cached:
            item['active'] = ''
            item['open'] = ''
            if len(item.get('items', [])) > 0:
                item['items'] = cls.resolve_menu_urls(request, modules, permissions, item['items'])
            else:
                item['items'] = []
            item['title'] = item['title']
            if item.get('required-permission', None) is None or cls.is_menu_visible(modules, permissions, item):
                if cls.is_url_covered(item['link'], request.c_request_path):
                    item['active'] = 'active'
                if 'default-params' in item:
                    first = True
                    for param in item['default-params']:
                        item['link'] += ('?' if first else '&') + param + '=' + item['default-params'][param]
                        first = False
                n_items += (item,)
            if len(list(filter(lambda a: a['active'] == 'active' or a['open'] == 'open', item['items']))) > 0:
                item['active'] = 'active'
                item['open'] = 'open'
            if len(item['items']) == 0 and item['link'] == '' and item in n_items:
                n_items.remove(item)
        return n_items

    @classmethod
    def is_url_covered(cls, url_1, url_2):
        url_2_cache = copy.deepcopy(url_2)
        while url_2_cache != '':
            if url_1 == url_2_cache or url_1 == url_2_cache + '/':
                return True

            url_2_cache = url_2_cache[:url_2_cache.rfind('/')]
        return False

    @classmethod
    def resolve_url(cls, request, url_name):
        if url_name is '' or url_name is None:
            return ''
        try:
            return reverse(url_name)
        except NoReverseMatch:
            return ''
