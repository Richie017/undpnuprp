import json
import re
from collections import OrderedDict

from django import template
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Max
from django.forms import HiddenInput
from django.template.exceptions import TemplateSyntaxError
from django.utils.html import escape
from django.utils.http import urlencode
from django.utils.translation import ugettext
from django_tables2.templatetags.django_tables2 import QuerystringNode, context_processor_error_msg
from widget_tweaks.templatetags.widget_tweaks import append_attr

from blackwidow.core.models.log.audit_log import DeletedEntityEnum
from blackwidow.core.models.permissions.modulepermission_assignment import ModulePermissionAssignment
from blackwidow.core.models.permissions.rolepermission_assignment import RolePermissionAssignment
from blackwidow.engine.constants.cache_constants import MODULE_PERMISSION_TIME_CACHE, ONE_MONTH_TIMEOUT, \
    ROLE_PERMISSION_TIME_CACHE
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import bw_titleize
from blackwidow.engine.extensions.list_extensions import inserted_list
from blackwidow.engine.extensions.menu_extensions import role_filify
from blackwidow.engine.managers.cachemanager import CacheManager

__author__ = 'Mahmud'

SITE_ROOT = settings.SITE_ROOT
MODEL_JASON_URL = settings.MODEL_JASON_URL
MENU_JASON_FILE_SUFFIX = settings.MENU_JASON_FILE_SUFFIX

register = template.Library()


@register.filter(name='has_next_level')
def has_next_level(value):
    _allowed_data_types = ['OrderedDict', 'dict']
    return True if type(value).__name__ in _allowed_data_types else False


@register.filter(name='is_hidden')
def filter_hidden(field):
    is_hidden = field.field.widget.__class__.__name__ == HiddenInput().__class__.__name__
    return is_hidden


@register.filter(name='is_datetime')
def filter_datetime(field):
    return 'date-time-picker' in field.field.widget.attrs.get('class', '').split(' ')


@register.filter(name='is_daterange')
def filter_datetime(field):
    return 'date-range-picker' in field.field.widget.attrs.get('class', '').split(' ')


@register.filter(name='get_property')
def filter_search_property(s, args):
    property = args.get('property', '')
    if property != '':
        return property
    return ''


@register.filter(name='get_prefix')
def get_prefix(prefix):
    if prefix == "" or prefix == '-' or prefix is None:
        return ""
    return prefix + '-'


@register.filter(name='replace_with_underscore')
def replace_prefix(s, r):
    if s == "" or s == r or s is None:
        return "_"
    return s.replace(r, '_')


@register.filter(name='name_value_pair')
def filter_dictionary(s, titleize=True):
    items = []
    for k in s:
        if 'detail_title' == k:
            continue
        items += [[bw_titleize(k) if titleize else k, s[k]]]
    return items


@register.filter(name='get_details_title')
def get_details_title(s, prop=None):
    try:
        title_key = 'details_view_title'
        properties_key = 'properties'
        if title_key in s and s[title_key]:
            return s[title_key]
        elif properties_key in s and s[properties_key]:
            return filter_dictionary_name(s[properties_key], prop=prop)
        else:
            return ''
    except:
        return ''


@register.filter(name="to_unified_lower")
def to_unified_lower(name):
    name = name.lower()
    return name.replace(' ', '_')


@register.filter(name="to_unified_lower_including_special")
def to_unified_lower_including_special(name):
    '''
    :param name: a string where we apply the filter
    :return: _ret_name which is unified lower name where special character except '_' is replaced with '_'
    '''

    _ret_name = ''
    for chr in name:
        if chr.isalnum() or chr == '_':
            _ret_name += chr.lower()
        else:
            _ret_name += '_'

    return _ret_name


@register.filter(name="to_unified_lower_excluded_special")
def to_unified_lower_excluded_special(name):
    '''
    :param name: a string where we apply the filter
    :return: name having only alphanumeric value and under score
    '''

    name = to_unified_lower(name)
    name = ''.join(e for e in name if e == '_' or e.isalnum())
    return name


@register.filter(name="tab_prefix_forms")
def tab_prefix_forms(form, tab_name):
    tab_fields = form.Meta.tabs[tab_name]
    return [x[1] for x in form.child_forms if x[2] and x[0] in tab_fields]


@register.filter(name="tab_suffix_forms")
def tab_suffix_forms(form, tab_name):
    tab_fields = form.Meta.tabs[tab_name]
    return [x[1] for x in form.child_forms if (not x[2]) and x[0] in tab_fields]


@register.filter(name="check_type")
def check_type(val):
    return type(val).__name_


@register.filter(name='is_range_input')
def filter_range_input(field):
    return 'range' in field.field.widget.attrs.get('class', '').split(' ')


@register.filter(name='apply_fields_grouping')
def apply_fields_grouping(s):
    _field_groups = s.field_groups()
    _field_group_dict = OrderedDict([('', list())])
    for _field in s:
        if bool(_field_groups):
            is_group_field = False
            for _group_name, _group_fields in _field_groups.items():
                if _group_name not in _field_group_dict.keys():
                    _field_group_dict[_group_name] = list()
                if _field.name in _group_fields:
                    _field_group_dict[_group_name].append(_field)
                    is_group_field = True
            if not is_group_field:
                _field_group_dict[''].append(_field)
        else:
            _field_group_dict[''].append(_field)
    return _field_group_dict


@register.filter(name='is_print_btn')
def is_print_btn(s):
    if s.startswith('Print'):
        return True
    return False


@register.filter(name='is_group_fields_in_tabs')
def is_group_fields_in_tabs(form_fields, tabs):
    for field in form_fields:
        if field.name in tabs:
            return True
    return False


@register.filter(name='get_name')
def filter_dictionary_name(s, prop=None):
    if prop:
        return s[prop]
    if 'name' in s:
        return s['name']
    if 'full_name' in s:
        return s['full_name']
    if 'detail_title' in s:
        return s['detail_title']
    return ''


@register.filter(name='is_selected')
def select_search_property(s, args):
    if s == args:
        return "selected=selected"
    return ''


@register.filter(name='get_search_value')
def get_search_value(s, args):
    property = args.get('query_1', '')
    if property != '':
        return "value=" + property + ""

    property = args.get('query_2', '')
    if property != '':
        return "value=" + property + ""

    return 'All'


@register.filter(name='add_prefix')
def add_prefix(field, args):
    return append_attr(field, 'data-prefix:' + str(args) + '-')


@register.filter(name='make_search_list')
def make_search_list(s):
    a = []
    for field, name, is_date in s:
        a.append((bw_titleize(name), field, is_date))
    return inserted_list(a, 0, ('Select one', 'all', False))


@register.filter(name='remove_quote')
def remove_quote(s):
    return str(s).strip('\'')


@register.filter(name='append_request')
def append_request(object, request):
    return {
        "request": request,
        "object": object
    }


@register.filter(name="filter_inline_object_permission")
def filter_inline_object_permission(object, buttons):
    # inline_buttons = object.get_inline_manage_buttons
    # model = get_model(object._meta.app_label, object.__class__.__name__)
    # buttons = model.get_manage_buttons()
    object_inline_buttons = buttons['object']
    request = buttons['request']
    inline_buttons = list()
    if not object_inline_buttons:
        return []
    for btn in object_inline_buttons:
        if btn == ViewActionEnum.Details:
            inline_buttons += [dict(
                name='Details',
                action='view',
                title="Click to view this item",
                icon='icon-eye',
                ajax='0',
                url_name=object.__class__.get_route_name(action=ViewActionEnum.Details),
                classes='all-action ',
                parent=None
            )]
        if btn == ViewActionEnum.SecureDownload:
            inline_buttons += [dict(
                name='Download',
                action='download',
                title="Click to download this item",
                icon='fa fa-download',
                ajax='0',
                url_name=object.__class__.get_route_name(action=ViewActionEnum.SecureDownload),
                classes='all-action ',
                parent=None
            )]
        if btn == ViewActionEnum.Edit:
            inline_buttons += [dict(
                name='Edit',
                action='edit',
                title="Click to edit this item",
                icon='icon-pencil',
                ajax='0',
                url_name=object.__class__.get_route_name(action=ViewActionEnum.Edit),
                classes='all-action',
                parent=None
            )]
        if btn == ViewActionEnum.Delete:
            inline_buttons += [dict(
                name='Delete',
                action='delete',
                title="Click to remove this item",
                icon='icon-remove',
                ajax='0',
                url_name=object.__class__.get_route_name(action=ViewActionEnum.Delete),
                classes='manage-action all-action confirm-action',
                parent=None
            )]
        if btn == ViewActionEnum.Mutate:
            inline_buttons += [dict(
                name='Accept',
                action='view',
                title="Click to accept this order",
                icon='icon-arrow-right',
                ajax='0',
                url_name=object.__class__.get_route_name(action=ViewActionEnum.Mutate),
                url_params={'pk': object.pk},
                classes='all-action confirm-action',
                parent=None
            )]
        if btn == ViewActionEnum.Approve:
            inline_buttons += [dict(
                name='Approve',
                action='approve',
                title="Click to approve this order",
                icon='icon-arrow-right',
                ajax='0',
                url_name=object.__class__.get_route_name(action=ViewActionEnum.Approve),
                url_params={'pk': object.pk},
                classes='all-action confirm-action',
                parent=None
            )]
        if btn == ViewActionEnum.Reject:
            inline_buttons += [dict(
                name='Reject',
                action='reject',
                title="Click to reject this order",
                icon='icon-arrow-right',
                ajax='0',
                url_name=object.__class__.get_route_name(action=ViewActionEnum.Reject),
                url_params={'pk': object.pk},
                classes='all-action confirm-action',
                parent=None
            )]
        if btn == ViewActionEnum.Activate:
            inline_buttons += [dict(
                name='Activate',
                action='activate',
                title="Click to re-activate this item",
                icon='icon-checkmark',
                ajax='0',
                url_name=object.__class__.get_route_name(action=ViewActionEnum.Activate),
                url_params={'pk': object.pk},
                classes='all-action confirm-action',
                parent=None
            )]
        if btn == ViewActionEnum.Deactivate:
            inline_buttons += [dict(
                name='Deactivate',
                action='deactivate',
                title="Click to deactivate this item",
                icon='icon-cancel-circle',
                ajax='0',
                url_name=object.__class__.get_route_name(action=ViewActionEnum.Deactivate),
                url_params={'pk': object.pk},
                classes='all-action confirm-action',
                parent=None
            )]

    if request.c_user.is_super:
        if hasattr(object, 'deleted_status') and object.deleted_status == DeletedEntityEnum.SoftDeleted.value:
            inline_buttons.append(dict(
                name='Restore',
                action='restore',
                title="Click to restore this item",
                icon='icon-redo icon-safe',
                ajax='0',
                url_name=object.__class__.get_route_name(action=ViewActionEnum.Restore),
                classes='all-action confirm-action',
                parent=None
            ))
            inline_buttons.append(dict(
                name='Delete',
                action='delete',
                title="Click to delete this item permanently",
                icon='icon-remove icon-danger',
                ajax='0',
                url_name=object.__class__.get_route_name(action=ViewActionEnum.Delete),
                classes='all-action confirm-action',
                parent=None,
                params='hard_delete=1'
            ))

    return inline_buttons


@register.filter(name="sorted_search_form")
def sorted_search_form(object):
    search_list = []

    for field in object:
        if not field.field.readonly:
            search_list.append(field)
    sorted_items = sorted(search_list, key=lambda a: a.label)
    return sorted_items


@register.filter(name='toggle_sorting_class')
def toggle_sorting_class(order_alias, request):
    sorted_params = request.GET.get("sorted_params")
    if sorted_params:
        sorted_params = json.loads(sorted_params.replace('\'', "\""))
        sort_param_name = sorted_params['sort']
        if sort_param_name.replace('-', '') == order_alias.replace('-', ''):
            if sort_param_name.startswith("-"):
                return sort_param_name.replace('-', '')
            else:
                return "-" + sort_param_name
    return order_alias


def token_kwargs(bits, parser):
    """
    Based on Django's `~django.template.defaulttags.token_kwargs`, but with a
    few changes:
    - No legacy mode.
    - Both keys and values are compiled as a filter
    """
    kwarg_re = re.compile(r"(?:(.+)=)?(.+)")
    if not bits:
        return {}
    kwargs = OrderedDict()
    while bits:
        match = kwarg_re.match(bits[0])
        if not match or not match.group(1):
            return kwargs
        key, value = match.groups()
        del bits[:1]
        kwargs[parser.compile_filter(key)] = parser.compile_filter(value)
    return kwargs


class ExtendedQStringNode(QuerystringNode):
    def render(self, context):
        if not 'request' in context:
            raise ImproperlyConfigured(context_processor_error_msg
                                       % 'querystring')
        params = {}
        get_dict = dict(context['request'].GET)
        for key, value in get_dict.items():
            if key != 'sorted_params':
                params[key] = value
        for key, value in self.updates.items():
            key = key.resolve(context)
            value = value.resolve(context)
            if key not in ("", None):
                params[key] = value
        for removal in self.removals:
            params.pop(removal.resolve(context), None)
        return escape("?" + urlencode(params, doseq=True))


@register.tag
def querystring_generator(parser, token):
    bits = token.split_contents()
    tag = bits.pop(0)
    updates = token_kwargs(bits, parser)
    # ``bits`` should now be empty of a=b pairs, it should either be empty, or
    # have ``without`` arguments.
    if bits and bits.pop(0) != "without":
        raise TemplateSyntaxError("Malformed arguments to '%s'" % tag)
    removals = [parser.compile_filter(bit) for bit in bits]
    querystring = ExtendedQStringNode(updates, removals)
    return querystring


@register.filter(name='toggle_sorting_icon')
def toggle_sorting_icon(column, request):
    column_alias_next = column.order_by_alias.next
    sorted_params = request.GET.get("sorted_params")
    if sorted_params:
        sorted_params = json.loads(sorted_params.replace('\'', "\""))
        sort_param_name = sorted_params['sort']
        if sort_param_name.replace('-', '') == column_alias_next.replace('-', ''):
            th = column.attrs['th']
            th_class = th['class']
            new_th_class = th_class_list = th_class.split()
            if not sort_param_name.startswith("-"):
                if 'desc' in th_class_list:
                    new_th_class = ['asc'] + [tc for tc in th_class_list if tc != 'desc']
                else:
                    new_th_class = ['asc'] + th_class_list
            else:
                if 'asc' in th_class_list:
                    new_th_class = ['desc'] + [tc for tc in th_class_list if tc != 'asc']
                else:
                    new_th_class = ['desc'] + th_class_list
            th['class'] = ' '.join(new_th_class)
            return th.as_html()
    new_attrs = column.attrs['th'].as_html()
    return new_attrs


class PaginationQStringNode(QuerystringNode):
    def render(self, context):
        if not 'request' in context:
            raise ImproperlyConfigured(context_processor_error_msg
                                       % 'querystring')
        params = {}
        get_dict = dict(context['request'].GET)
        for key, value in get_dict.items():
            if key != 'sorted_params' and key != 'page':
                params[key] = value
            elif key == 'sorted_params':
                v = value[0] if value else ""
                v = v.replace("'", '"')
                import json
                vjson = json.loads(v)
                for key, val in vjson.items():
                    params[key] = val
        for key, value in self.updates.items():
            key = key.resolve(context)
            value = value.resolve(context)
            if key not in ("", None) and not key in params.keys():
                params[key] = value
        for removal in self.removals:
            params.pop(removal.resolve(context), None)
        return escape("?" + urlencode(params, doseq=True))


# {% querystring "name"="abc" "age"=15 %}
@register.tag
def ext_querystring(parser, token):
    """
    Creates a URL (containing only the querystring [including "?"]) derived
    from the current URL's querystring, by updating it with the provided
    keyword arguments.

    Example (imagine URL is ``/abc/?gender=male&name=Brad``)::

        {% querystring "name"="Ayers" "age"=20 %}
        ?name=Ayers&gender=male&age=20
        {% querystring "name"="Ayers" without "gender" %}
        ?name=Ayers

    """
    bits = token.split_contents()
    tag = bits.pop(0)
    updates = token_kwargs(bits, parser)
    # ``bits`` should now be empty of a=b pairs, it should either be empty, or
    # have ``without`` arguments.
    if bits and bits.pop(0) != "without":
        raise TemplateSyntaxError("Malformed arguments to '%s'" % tag)
    removals = [parser.compile_filter(bit) for bit in bits]
    return PaginationQStringNode(updates, removals)


@register.filter(name='translate')
def translate(text):
    try:
        return ugettext(text)
    except:
        return text


@register.filter(name='get_role_menu_js')
def get_role_menu_js(base_url, user):
    try:
        role_name = user.consoleuser.role.name
        module_last_updated = CacheManager.get_from_cache_by_key(key=MODULE_PERMISSION_TIME_CACHE)
        if module_last_updated is None:
            module_last_updated = ModulePermissionAssignment.objects.aggregate(Max('last_updated'))['last_updated__max']
            CacheManager.set_cache_element_by_key(key=MODULE_PERMISSION_TIME_CACHE, value=module_last_updated,
                                                  timeout=ONE_MONTH_TIMEOUT)
        permission_last_updated = CacheManager.get_from_cache_by_key(key=ROLE_PERMISSION_TIME_CACHE)
        if permission_last_updated is None:
            permission_last_updated = RolePermissionAssignment.objects.aggregate(Max('last_updated'))[
                'last_updated__max']
            CacheManager.set_cache_element_by_key(key=ROLE_PERMISSION_TIME_CACHE, value=permission_last_updated,
                                                  timeout=ONE_MONTH_TIMEOUT)
        version = module_last_updated \
            if module_last_updated > permission_last_updated else permission_last_updated
        return MODEL_JASON_URL + 'roles/' + role_filify(role_name) + MENU_JASON_FILE_SUFFIX + '?version=' + str(version)
    except:
        return base_url + 'no-role-menu.js'
