import json
from urllib import parse

from django.db import models
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.http.request import QueryDict

from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.routers.database_router import BWDatabaseRouter


class CQuerySet(QuerySet):
    def __init__(self, model=None, cache=None):
        query = None
        using = None
        hints = None
        super(CQuerySet, self).__init__(model=model, using=using)
        self._result_cache = cache

    def order_by(self, *field_names):
        qs = super(CQuerySet, self).order_by(*field_names)
        if self._result_cache is not None:
            qs._result_cache = [obj for obj in self._result_cache]
            for field in field_names:
                qs._result_cache.sort(key=lambda obj: getattr(obj, field))
        return qs


class ProtectedQuerySetMixin(object):
    model = None
    request = None

    @classmethod
    def build_search_fields(cls, model=None, columns=None, **kwargs):
        filters = tuple()
        all_props = dir(model)
        exclude_list = model.exclude_search_fields()
        for c in columns:
            field_name = c.name
            if c.name.startswith('render_'):
                field_name = c.name.replace('render_', '')

            if c.name in exclude_list:
                continue

            try:
                field = model._meta.get_field(field_name)
                if isinstance(field, (models.CharField, models.TextField, models.OneToOneField, models.ForeignKey)):
                    filters += ((field.name, c.verbose_name, False),)
                elif isinstance(field, (models.DateTimeField, models.DateField,)):
                    filters += ((field.name, c.verbose_name, True),)
                elif field.name in model.get_datetime_fields():
                    filters += ((field.name, c.verbose_name, True),)
            except:
                if c.name in all_props and c.name.startswith("render_"):
                    if field_name in model.get_datetime_fields():
                        filters += ((c.name.replace("render_", "__search_"), field_name, True),)
                    else:
                        filters += ((c.name.replace("render_", "__search_"), field_name, False),)
        return filters

    def clear_sort_parameters(self, request):
        data_dict = request.GET
        refined_GET = {}
        sort_dict = {}
        decision_tried = False
        for key, value in data_dict.items():
            if key == "sort":
                sort_dict[key] = value
            else:
                refined_GET[key] = value

            decision_tried = True
        if not refined_GET and not decision_tried:
            return request.GET, {}
        if sort_dict:
            refined_GET["sorted_params"] = sort_dict
        params = parse.urlencode(refined_GET)
        qdict = QueryDict(params)
        return qdict, sort_dict

    def append_parameters(self, request, parameters):
        data_dict = request.GET
        refined_GET = {}
        for key, value in data_dict.items():
            refined_GET[key] = value
        for key, value in parameters.items():
            refined_GET[key] = value
        params = parse.urlencode(refined_GET)
        qdict = QueryDict(params)
        return qdict

    def add_sign_prefix(self, descending_sorts, field_name):
        if descending_sorts.get(field_name.replace('-', '')):
            if not field_name.startswith('-'):
                return '-' + field_name
            else:
                return field_name
        else:
            if field_name.startswith('-'):
                return field_name.replace('-', '')
            else:
                return field_name

    def apply_distinct(self, queryset=None, **kwargs):
        if hasattr(self.model, "distinct_fields"):
            if not (ViewActionEnum.Details.value in self.request.path or
                            ViewActionEnum.Delete.value in self.request.path):
                # TODO: Update with regular expression, to avoid hastle processing model name containing 'details'
                distinct_fields = [f for f in getattr(self.model, "distinct_fields")()]
                orderables = list(distinct_fields)
                order_by = self.model.default_order_by()
                if type(order_by) == str:
                    orderables += [order_by]
                else:
                    orderables += list(order_by)
                _queryset = queryset.order_by(*orderables)
                item_ids = _queryset.distinct(*distinct_fields).values_list('pk', flat=True)
                queryset = queryset.model.objects.filter(pk__in=item_ids)

                # TODO The following order by is redundant. This has been required to apply distinct in the ordered
                # queryset and then again ordering it in required order. Will be handful to get a work around here
                if type(order_by) == str:
                    queryset = queryset.order_by(order_by)
                else:
                    order_by = list(order_by)
                    queryset = queryset.order_by(*order_by)
        return queryset

    def choose_database(self, request, **kwargs):
        return BWDatabaseRouter.get_default_database_name()

    def get_queryset(self, **kwargs):
        """
        This method is used to generate appropriate queryset for current request
        :param kwargs:
        Options for queryset generation
        :return:
        returns an appropriate queryset
        """
        _user = self.request.c_user.to_business_user()
        _add_versions = kwargs.get("add_versions", False)
        sort_param = None
        if self.request.GET.get('sort'):
            sort_param = self.request.GET.get('sort')
        elif self.request.GET.get('sorted_params'):
            sort_param = json.loads(self.request.GET.get('sorted_params').replace("'", '"')).get('sort')

        self.request.GET, self.sort_param_dict = self.clear_sort_parameters(self.request)

        _db_label = self.choose_database(request=self.request)

        if _add_versions:
            # Adding custom filter to manager
            try:
                if self.model.objects._filter:
                    if not self.model.objects_include_versions._filter:
                        self.model.objects_include_versions._filter = {}
                    self.model.objects_include_versions._filter.update(self.model.objects._filter)

                if self.model.objects._exclude:
                    if not self.model.objects_include_versions._exclude:
                        self.model.objects_include_versions._exclude = {}
                    self.model.objects_include_versions._exclude.update(self.model.objects._exclude)
            except:
                pass
            _queryset = self.model.get_queryset(
                queryset=self.model.objects_include_versions.filter_organization(
                    organization_id=_user.organization_id).all(), user=_user,
                profile_filter=not (_user.is_super))
        else:
            _queryset = self.model.get_queryset(
                queryset=self.model.objects.filter_organization(organization_id=_user.organization_id).all(),
                user=_user,
                profile_filter=not (_user.is_super))
        _queryset = _user.filter_model(request=self.request, queryset=_queryset, database=_db_label)
        _queryset = self.model.apply_search_filter(search_params=self.request.GET, queryset=_queryset, **kwargs)

        # Prefetch related objects
        if self.model.prefetch_objects():
            _queryset = _queryset.prefetch_related(*self.model.prefetch_objects())

        try:
            if sort_param:

                descending_sorts = {
                    sort_param.replace('-', ''): sort_param.startswith('-')
                }

                _field_name = sort_param.replace("-", "").replace("render_", "")
                _field_name = _field_name.split(":")[0]
                try:
                    _field = self.model._meta.get_field(_field_name.replace("-", ""))
                except:
                    _field = None
                order_by_filter = []
                if _field:
                    if isinstance(_field, models.ForeignKey) or isinstance(_field, models.ManyToManyField):
                        if hasattr(_field.remote_field.model, "order_by_%s" % _field_name.replace('-', '')):
                            order_by_filter = getattr(_field.remote_field.model,
                                                      "order_by_%s" % _field_name.replace('-', ''))()
                            temp_filters = []
                            for of in order_by_filter:
                                if descending_sorts.get(_field.name.replace('-', '')):
                                    if not of.startswith('-'):
                                        temp_filters += ['-' + of]
                                    else:
                                        temp_filters += [of]
                                else:
                                    if of.startswith('-'):
                                        temp_filters += [of.replace('-', '')]
                                    else:
                                        temp_filters += [of]
                            order_by_filter = temp_filters
                        else:
                            try:
                                _name = _field.remote_field.model._meta.get_field('name')
                            except Exception as exp:
                                _name = None
                            if _name:
                                order_by_filter = [self.add_sign_prefix(descending_sorts, _field.name) + "__name"]
                            else:
                                order_by_filter = []
                    else:
                        if descending_sorts.get(sort_param.replace('-', '')):
                            if not _field_name.startswith('-'):
                                order_by_filter = ['-' + _field_name]
                            else:
                                order_by_filter = [_field_name]
                        else:
                            if _field_name.startswith('-'):
                                order_by_filter = [_field_name.replace('-', '')]
                            else:
                                order_by_filter = [_field_name]
                else:
                    if hasattr(_queryset.model, "order_by_%s" % sort_param.replace("-", "").replace("render_", "")):
                        order_by_filter = getattr(_queryset.model,
                                                  "order_by_%s" % sort_param.replace("-", "").replace("render_", ""))()
                        temp_filters = []
                        for of in order_by_filter:
                            if descending_sorts.get(sort_param.replace('-', '')):
                                if not of.startswith('-'):
                                    temp_filters += ['-' + of]
                                else:
                                    temp_filters += [of]
                            else:
                                if of.startswith('-'):
                                    temp_filters += [of.replace('-', '')]
                                else:
                                    temp_filters += [of]
                        order_by_filter = temp_filters
                    else:
                        order_by_filter = []

                _queryset = _queryset.order_by(*order_by_filter)

            else:
                order_by = self.model.default_order_by()
                if type(order_by) == str:
                    _queryset = _queryset.order_by(order_by)
                else:
                    order_by = list(order_by)
                    _queryset = _queryset.order_by(*order_by)
            _queryset = self.apply_distinct(queryset=_queryset)
            return _queryset
        except Exception as exp:
            return _queryset.filter(is_version=False).using(self.choose_database(request=self.request))

    def get_api_queryset(self, queryset=None, **kwargs):
        """
        Generate appropriate queryset for API request. The approach is to generate generic queryset and then apply mobile based filters.
        :param queryset:
        Base queryset
        :param kwargs:
        options for queryset generation
        :return:
        an appropriate queryset
        """

        # Prefetch related objects
        if self.model.prefetch_api_objects():
            queryset = queryset.prefetch_related(*self.model.prefetch_api_objects())

        api_filters = self.model.get_api_filters()
        if api_filters is not None:
            queryset = queryset.filter(Q(**api_filters))
        return self.model.get_model_api_queryset(queryset=queryset).using(
            self.choose_database(request=self.request))  # Apply api specific queryset
