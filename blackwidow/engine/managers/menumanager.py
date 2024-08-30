import importlib

from django.apps import apps
from django.urls import path
from django.conf.urls import url

from blackwidow.engine.constants.access_permissions import BW_ACCESS_READ_ONLY
from blackwidow.engine.decorators.utility import get_models_with_decorator
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.exceptions.exceptions import BWException
from blackwidow.engine.extensions.bw_titleize import bw_titleize
from blackwidow.engine.extensions.model_descriptor import get_model_by_name
from blackwidow.engine.managers.formmanager import FormManager
from config.apps import INSTALLED_APPS

get_model = apps.get_model

__author__ = 'Mahmud'


class MenuManager(object):
    @classmethod
    def attributes(cls):
        return ['hide']

    @classmethod
    def child_item_attribute(cls):
        return 'items'

    @classmethod
    def remove_blanks(cls, menu_item):
        if 'items' in menu_item:
            sorted_items = sorted(menu_item['items'], key=lambda a: a['title'])
            if len(sorted_items) > 0:
                sorted_items[0]['section'] = 'section'
                result = []
                for item in sorted_items:
                    result += cls.remove_blanks(item)
                menu_item['items'] = result
            else:
                menu_item['items'] = sorted_items

            if menu_item['link'] == '':
                return menu_item['items']
        return [menu_item]

    @classmethod
    def sort_items(cls, menu_item):
        if 'items' in menu_item:
            sorted_items = sorted(menu_item['items'], key=lambda a: a['order'])
            if len(sorted_items) > 0:
                result = []
                for item in sorted_items:
                    result += cls.sort_items(item)
                menu_item['items'] = result
            else:
                menu_item['items'] = sorted_items
        return [menu_item]

    @classmethod
    def get_view_dict(cls):
        all_modules = []
        all_forms = dict()
        for app in INSTALLED_APPS:
            forms = app + '.views'
            try:
                all_modules.append(importlib.import_module(forms))
            except ImportError as err:
                print(err)
            except Exception as err:
                print(err)
        for module in all_modules:
            all_attrs = [x for x in dir(module) if x.endswith('View')]
            for _attr in all_attrs:
                try:
                    _form = getattr(module, _attr)
                    if 'get_view_meta' in dir(_form) and bool(_form.get_view_meta('override_view', 'model')):
                        all_forms[_form.get_view_meta('override_view', 'model').__name__ + '_' + str(
                            _form.get_view_meta('override_view', 'view'))] = _form
                except ImportError as err:
                    print(err)
                except Exception as err:
                    print(err)
        return all_forms

    @classmethod
    def get_view_class(cls, model_name, view_dict=None, default=None, **kwargs):
        if view_dict is None:
            view_dict = cls.get_view_dict()
        if model_name not in view_dict:
            return default
        return view_dict[model_name]

    @classmethod
    def generate_menu_dict(cls, append_dummy_module=True, **kwargs):
        routed_models = get_models_with_decorator('route', INSTALLED_APPS, include_class=True)
        menu_config = []
        for _m in routed_models:
            # if _m.get_model_meta('route', 'hide') == True:
            #     continue

            module = _m.get_model_meta('route', 'module')
            if module is None or _m.get_model_meta('route', 'hide') == True:
                continue

            _rc = dict()
            _rc['hide'] = _m.get_model_meta('route', 'hide')
            _rc['link'] = '/' + _m.get_model_meta('route', 'route') + '/'
            _rc['title'] = _m.get_model_meta('route', 'display_name') if _m.get_model_meta('route',
                                                                                           'display_name') is not None else bw_titleize(
                _m.__name__)
            _rc['order'] = _m.get_model_meta('route', 'item_order') if _m.get_model_meta('route',
                                                                                         'item_order') else 1000
            _rc['required-permission'] = list()
            _rc['required-permission'].append(dict(
                app=_m._meta.app_label,
                context=_m.__name__,
                access=int(BW_ACCESS_READ_ONLY['value'])
            ))

            existing_modules = list(filter(lambda x: x['title'] == module.value.get('title', ''), menu_config))
            if len(existing_modules) > 0:
                existing_module = existing_modules[0]
            else:
                existing_module = dict()
                existing_module['title'] = module.value['title']
                existing_module['link'] = '/' + module.value['route'] + '/dashboard'
                existing_module['items'] = []
                existing_module['order'] = module.value['order']
                # existing_module['icon'] = module.value['icon']
                menu_config.append(existing_module)

            group = _m.get_model_meta('route', 'group')
            if group is not None:
                if isinstance(group, (list, tuple)):
                    t_groups = existing_module['items']
                    for g in group:
                        existing_groups = list(filter(lambda x: x['title'] == g, t_groups))
                        if len(existing_groups) > 0:
                            existing_group = existing_groups[0]
                        else:
                            existing_group = dict()
                            existing_group['title'] = g
                            existing_group['link'] = ''
                            existing_group['order'] = _m.get_model_meta('route', 'group_order')
                            existing_group['items'] = []
                            t_groups.append(existing_group)
                        t_groups = existing_group['items']
                        # existing_module['items'] = t_groups
                else:
                    existing_groups = list(filter(lambda x: x['title'] == group, existing_module['items']))
                    if len(existing_groups) > 0:
                        existing_group = existing_groups[0]
                    else:
                        existing_group = dict()
                        existing_group['title'] = group
                        existing_group['link'] = ''
                        existing_group['order'] = _m.get_model_meta('route', 'group_order') if _m.get_model_meta(
                            'route', 'group_order') else 1000
                        existing_group['items'] = []
                        existing_module['items'].append(existing_group)
            else:
                existing_group = existing_module

            existing_group['items'] += [_rc]

        # ... add overridden views
        # override_views = get_views_with_decorator('override_view', INSTALLED_APPS, include_class=True)

        modules = []  # [ModuleEnum.Help, ModuleEnum.Analysis, ModuleEnum.Reports, ModuleEnum.Settings]
        for m in modules:
            if len(list(filter(lambda x: x['title'] == m.value['title'], menu_config))) == 0:
                n_module = dict()
                n_module['title'] = m.value['title']
                n_module['link'] = '/' + m.value['route'] + '/dashboard'
                n_module['items'] = []
                n_module['order'] = m.value['order']
                menu_config.append(n_module)
        if len(menu_config) > 0:
            result = []
            for item in menu_config:
                result += cls.sort_items(item)
            return sorted(result, key=lambda a: a['order'])
        return menu_config

    @classmethod
    def generate_urls(cls, operations, **kwargs):
        form_dict = FormManager.get_form_dict()
        view_dict = cls.get_view_dict()
        routed_models = get_models_with_decorator('route', INSTALLED_APPS, include_class=True)
        partial_routed_models = get_models_with_decorator('partial_route', INSTALLED_APPS, include_class=True)
        urlpatterns = []

        for _m in routed_models:
            actions = _m.get_model_meta('route', 'actions') if _m.get_model_meta('route',
                                                                                 'actions') is not None else _m.get_routes()
            model_name = _m.get_model_meta('route', 'display_name') if _m.get_model_meta('route',
                                                                                         'display_name') is not None else bw_titleize(
                _m.__name__).lower()
            form_class = FormManager.get_form_class(_m, form_dict)
            # print('===> Model Name: '+model_name)
            for a in actions:
                f_operations = list(filter(lambda x: x[0] == a, operations))
                
                if len(f_operations) > 0:
                    o = f_operations[0]
                    view_class = cls.get_view_class(_m.__name__ + '_' + str(o[0]), view_dict, o[4])
                    route_name = _m.__name__.lower() + '_' + str(o[0])
                    success_url_name = _m.__name__.lower() + '_' + str(o[2])
                    route_url = _m.get_model_meta('route', 'route') + o[1]
                    
                    if o[2]:
                        urlpatterns += [path('' + route_url,
                                            view_class.as_view(model=_m, form_class=form_class, model_name=model_name,
                                                               success_url_name=success_url_name), name=route_name)]
                    else:
                        urlpatterns += [path('' + route_url, view_class.as_view(model=_m, model_name=model_name,
                                                                                 success_url_name=success_url_name),
                                            name=route_name)]
                else:
                    raise BWException('Route not found with key' + str(a))

        for _m in partial_routed_models:  # generate partial urls
            actions = _m.get_routes(partial=True)
            child_models = _m.get_model_meta('partial_route', 'models')
            for child_model in child_models:
                if isinstance(child_model, str):
                    if '.' in child_model:
                        child_model = get_model(child_model.split('.')[0], child_model.split('.')[1])
                    else:
                        child_model = get_model_by_name(child_model)
                model_name = child_model.get_model_meta('route', 'display_name') if child_model.get_model_meta('route',
                                                                                                               'display_name') is not None else bw_titleize(
                    child_model.__name__).lower()
                form_class = FormManager.get_form_class(child_model, form_dict)

                for a in actions:
                    f_operations = list(filter(lambda x: x[0] == a, operations))
                    if len(f_operations) > 0:
                        o = f_operations[0]
                        view_class = cls.get_view_class(_m.__name__ + '_' + str(o[0]), view_dict, o[4])
                        route_name = _m.__name__.lower() + '_' + child_model.__name__.lower() + '_' + str(o[0])
                        success_url_name = child_model.__name__.lower() + '_' + str(o[2])
                        route_url = child_model.get_model_meta('route', 'route') + o[1]
                        _t_model = child_model if o[0] == ViewActionEnum.PartialEdit else _m
                        # print('>>Partial Route Name :'+route_name)
                        if o[2]:
                            urlpatterns += [url(r'^_partial/' + _m.__name__.lower() + '/' + route_url,
                                                view_class.as_view(model=_t_model, form_class=form_class,
                                                                   model_name=model_name,
                                                                   success_url_name=success_url_name), name=route_name)]
                        else:
                            urlpatterns += [url(r'^_partial/' + _m.__name__.lower() + '/' + route_url,
                                                view_class.as_view(model=_t_model, model_name=model_name,
                                                                   success_url_name=success_url_name), name=route_name)]
                    else:
                        raise BWException('Route not found with key' + a)

        return urlpatterns
