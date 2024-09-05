from django.apps.registry import apps
from django.db import models
from django.core.exceptions import FieldDoesNotExist

from blackwidow.engine.extensions.bw_titleize import bw_titleize
from blackwidow.engine.extensions.clock import Clock
from blackwidow.engine.extensions.query_normalize import get_query

__author__ = 'Mahmud'


class SearchableModelMixin(object):
    @classmethod
    def exclude_search_fields(cls):
        return []

    @classmethod
    def get_url_by_name(cls, name):
        return None

    @classmethod
    def get_custom_search_str(cls, field_name, search_prefix='__search_'):
        return None

    @classmethod
    def build_single_filter(cls, model, prop, query_strings, prefix='', **kwargs):
        if prop.find(':') == -1:
            try:
                field = model._meta.get_field(prop)
                if isinstance(field, models.AutoField):
                    entry_query = get_query([int(q) for q in query_strings], [prefix + prop], _in=True)
                elif isinstance(field, models.ForeignKey):
                    entry_query = cls.build_query(field.remote_field.model, 'all', query_strings,
                                                  prefix=prefix + field.name + '__')
                elif isinstance(field, models.ManyToManyField):
                    pass
                elif isinstance(field, models.DecimalField):
                    entry_query = get_query([float(q) for q in query_strings], [prefix + prop],
                                            range=len(query_strings) > 1)
                elif isinstance(field, (models.BigIntegerField, models.IntegerField)):
                    entry_query = get_query([int(float(q)) for q in query_strings], [prefix + prop],
                                            range=len(query_strings) > 1)
                elif isinstance(field, models.BooleanField):
                    entry_query = get_query([bool(q) for q in query_strings], [prefix + prop])
                else:
                    entry_query = get_query(query_strings, [prefix + prop])
            except FieldDoesNotExist:
                entry_query = get_query(query_strings, [prefix + prop])
        else:
            property_list = prop.split(':')
            field = model._meta.get_field(property_list[0])
            entry_query = cls.build_single_filter(field.remote_field.model, ":".join(property_list[1:]),
                                                  query_strings, prefix=prefix + property_list[0] + '__')
        return entry_query

    @classmethod
    def build_query(cls, model, prop, query_strings, prefix='', **kwargs):
        if prop.lower() == 'all':
            if not prefix:
                fields = model.searchable_tabls_columns()
            else:
                fields = model.searchables()
            render_fields = [f for f in fields if f.startswith("render_")]
            fields = list(set(fields) - set(render_fields))
            if len(fields) > 0:
                entry_query = cls.build_single_filter(model, fields.pop(0), query_strings, prefix=prefix)
                for f in fields:
                    entry_query |= cls.build_single_filter(model, f, query_strings, prefix=prefix)
            else:
                return get_query(query_strings, ['pk'])
            for render_field in render_fields:
                field_name = render_field.replace('render_', '')
                property = cls.get_custom_search_str(field_name)
                if property:
                    entry_query |= get_query(query_strings, [property])
        else:
            entry_query = cls.build_single_filter(model, prop, query_strings, prefix=prefix)
        return entry_query

    @classmethod
    def get_search_fields(cls, search_params):
        """
        Get list of search parameters
        :param search_params: a dictionary, generally request.GET
        :return: list of search fields
        """
        search_fields = list()
        if search_params and search_params.get('search', '0') == '1':
            ignore = ['search', 'paginate_by', 'sort', 'page', 'depth', 'expand', 'format', 'authkey',
                      'disable_pagination', 'operator', 'csrfmiddlewaretoken']
            for key in [key for key in search_params if
                        not key.startswith("_search") and not key.startswith("__search") and not key in ignore]:
                search_value = list()
                value = list(filter(lambda x: x.strip() != '', search_params.get(key).split(',')))
                if key in cls.get_datetime_fields():
                    for v in value:
                        try:
                            v = int(v)
                        except Exception as exp:
                            v = Clock.get_timestamp_from_date(v)
                        search_value.append(str(v))
                    if len(search_value) == 1:
                        search_value.append(str(Clock.timestamp()))
                else:
                    search_value = value
                search_fields.append((key, search_value))
        return search_fields

    @classmethod
    def get_search_value(cls, field, search_fields, fields):
        from datetime import datetime

        is_range = False
        if len(fields) > 0:
            try:
                value = [v for x, v in fields if x == field][0]
            except:
                value = []
        else:
            value = []

        if field.lower() != "all":
            field_split = field.split(":")
            if len(field_split) > 1:
                search_list = [x for x in search_fields if x[0] == field_split[0]]
                if search_list:
                    is_range = search_list[0][2]
                    label = search_list[0][1] + ': ' + field.split(":")[1]
                else:
                    label = field_split[0] + ': ' + field.split(":")[1]
            else:
                search_list = [x for x in search_fields if x[0] == field_split[0]]
                if search_list:
                    is_range = search_list[0][2]
                    label = bw_titleize(search_list[0][1])
                else:
                    label = field_split[0]
        else:
            label = "All"
        values = list()
        if is_range:
            i = 0
            while i < len(value) / 2:
                if len(value[i]) > 1:
                    start_time = datetime.fromtimestamp(float(value[i]) / 1000.0).strftime('%d/%m/%Y %H:%M:%S')
                    end_time = datetime.fromtimestamp(float(value[i + 1]) / 1000.0).strftime('%d/%m/%Y %H:%M:%S')
                    values.append(start_time + ',' + end_time)
                    i += 2
        else:
            for _v in value:
                if len(_v) > 0:
                    values.append(_v)
        return label, values

    @classmethod
    def get_search_form(cls, search_fields, fields, custom_search_fields=[]):
        from blackwidow.core.generics.forms.search_form import GenericSearchForm
        from django import forms

        sf_class = type(
            'RunTime_' + cls.__name__ + '_SearchForm',
            (GenericSearchForm,),
            dict()
        )
        sf_instance = sf_class()
        for f, v in fields:
            if f == "sorted_params":
                continue
            label, values = cls.get_search_value(f, search_fields, fields)
            if f in sf_instance.fields:
                sf_instance.fields[f].initial += "," + values
            else:
                sf_instance.fields[f] = forms.CharField(label=bw_titleize(label), initial=values,
                                                        widget=forms.TextInput(attrs={'readonly': 'readonly'}))
                sf_instance.fields[f].readonly = True
        for f, v in custom_search_fields:
            label = f.replace("__search_", "").replace("__search", "").replace("_search_", "").replace("_search", "")
            label = ' '.join(label.split("_"))
            sf_instance.fields[f] = forms.CharField(label=bw_titleize(label), initial=[v],
                                                    widget=forms.TextInput(attrs={'readonly': 'readonly'}))
            sf_instance.fields[f].readonly = True
        return sf_instance

    @classmethod
    def get_custom_search_fields(cls, search_params):
        """
        this method is used to find out custom search fields from request
        :param search_params: a dictionary (generally request.GET)
        :return:
        """
        if search_params is None:
            return []

        _fields = []
        for key, value in search_params.items():
            if key.startswith("_search") or key.startswith("__search"):
                _fields += [(key, value,)]
        return _fields

    @classmethod
    def filter_search_query(cls, query_set, custom_search_fields):
        all_fields = dir(query_set.model)
        for key, value in custom_search_fields:
            key = key.replace("__search_", "search_")
            if key in all_fields:
                if key.replace("search_", "render_") in query_set.model.get_datetime_fields():
                    try:
                        value1, value2 = value.split(',')
                        ts1 = Clock.get_timestamp_from_date(value1)
                        ts2 = Clock.get_timestamp_from_date(value2)
                        query_set = getattr(query_set.model, key)(query_set, ts1, ts2)
                    except Exception as exp:
                        _ErrorLog = apps.get_model("core", "ErrorLog")
                        _ErrorLog.log("Exception occurred while tried to search using a custom datetime range field. "
                                      "Message: %s and params: %s" % (str(exp), value))
                else:
                    query_set = getattr(query_set.model, key)(query_set, value)
        return query_set

    @classmethod
    def collect_custom_search_queries_for_model(cls, queryset, value):
        model = queryset.model
        all_fields = dir(model)
        query_list = []
        table_columns = model.table_columns()
        exclude_fields = model.exclude_search_fields()
        searchable_fields = tuple(set(table_columns) - set(exclude_fields))
        for s_field in searchable_fields:
            sfield = s_field
            if sfield.startswith("render_"):
                sfield = sfield.replace("render_", "")
                search_field = "search_" + sfield
                if search_field in all_fields:
                    if search_field.replace("search_", "render_") in queryset.model.get_datetime_fields():
                        try:
                            value1, value2 = value[0], value[1]
                            ts1 = Clock.get_timestamp_from_date(value1)
                            ts2 = Clock.get_timestamp_from_date(value2)
                            query_set = getattr(queryset.model, search_field)(queryset, ts1, ts2)
                            query_list += [query_set]
                        except Exception as exp:
                            _ErrorLog = apps.get_model("core", "ErrorLog")
                            _ErrorLog.log(
                                "Exception occurred while tried to search using a custom datetime range field."
                                " Message: %s and params: %s" % (str(exp), value))
                    else:
                        query_set = getattr(queryset.model, search_field)(queryset, value[0])
                        query_list += [query_set]
        return query_list

    @classmethod
    def apply_all_search_custom_fields(cls, queryset, qset_compare, value):
        query_list = queryset.model.collect_custom_search_queries_for_model(queryset, value)
        for qset in query_list:
            qset_compare |= qset
        return qset_compare

    @classmethod
    def apply_search_filter(cls, search_params=None, queryset=None, **kwargs):
        """
        apply search filter on queryset based on the search params provided in request
        :param search_params: a dictionary, generally request.GET
        :param queryset: queryset on which filtering should be applied
        :param kwargs: extra params
        :return: queryset with seach filters applied
        """
        if queryset is None:
            queryset = cls.objects.none()
        _custom_search_fields = cls.get_custom_search_fields(search_params=search_params)
        s_fields = cls.get_search_fields(search_params=search_params)
        if search_params and search_params.get('search', '0') == '1':
            for key, value in s_fields:
                if len(value) > 0:
                    queryset_1 = queryset
                    entry_query = cls.build_query(queryset.model, key, value)
                    if entry_query is not None:
                        try:
                            queryset = queryset.filter(entry_query)
                        except Exception:
                            pass
                    if key.lower() == 'all':
                        queryset_2 = queryset_1.model.apply_all_search_custom_fields(
                            queryset=queryset_1, qset_compare=queryset, value=value)
                        queryset = queryset | queryset_2
            try:
                queryset = cls.filter_search_query(queryset, _custom_search_fields)
                queryset = queryset.model.filter_query(queryset, _custom_search_fields)
            except Exception as exp:
                pass
        return queryset