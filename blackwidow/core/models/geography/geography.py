from collections import OrderedDict

from django.db import models
from django.db.models.query_utils import Q
from django.utils.safestring import mark_safe
from rest_framework import serializers

from blackwidow.core.models.contracts.configurabletype import ConfigurableType
from blackwidow.engine.decorators.enable_caching import enable_caching
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context, save_audit_log
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'Tareq'


@decorate(expose_api('geography'), is_object_context,
          save_audit_log, enable_caching(),
          route(route='geography', group='Address', group_order=2, module=ModuleEnum.Settings,
                display_name="Address", hide=True))
class Geography(ConfigurableType):
    level = models.ForeignKey('core.GeographyLevel', null=True, on_delete=models.SET_NULL)
    parent = models.ForeignKey('core.Geography', null=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'core'

    def get_choice_name(self):
        if self.level.name == 'Ward':
            return str(self.parent.name + '-' + self.name)
        return str(self.name)

    @property
    def select2_string(self):
        if self.level.name == 'Ward':
            return str(self.parent.name + '-' + self.name)
        return str(self.name)

    @classmethod
    def default_order_by(cls):
        return 'name'

    def to_json(self, depth=0, expand=None, wrappers=[], conditional_expand=[], **kwargs):
        obj = super().to_json(depth=0, expand=None, wrappers=[], conditional_expand=[], **kwargs)
        obj['select2_string'] = self.select2_string
        return obj

    def to_model_data(self):
        model_data = super(Geography, self).to_model_data()
        model_data['id'] = self.pk
        model_data['name'] = self.name if not self.level.name == 'Ward' else self.parent.name + '-' + self.name
        model_data['parent'] = self.parent_id if self.parent is not None else None
        return model_data

    @classmethod
    def get_model_data_query(cls):
        return Q(level__name='Division') | Q(level__name='Pourashava/City Corporation') | Q(level__name='Ward')

    @property
    def render_parent_type(self):
        return self.parent.type if self.parent else 'N/A'

    @classmethod
    def table_columns(cls):
        return [
            'render_code', 'name', 'type', 'parent', 'render_parent_type',
            'created_by', 'date_created', 'last_updated'
        ]

    @property
    def details_config(self):
        details = OrderedDict()
        details['code'] = self.code
        details['name'] = self.name
        details['level'] = self.level
        if self.parent:
            details[self.parent.type] = self.parent
        details['created_by'] = self.created_by
        details['date_created'] = self.render_timestamp(self.date_created)
        details['last_updated_by'] = self.last_updated_by
        details['last_updated'] = self.render_timestamp(self.last_updated)

        return details

    def get_success_url(self, request):
        return '/' + self.__class__.get_model_meta(
            'route', 'route') + '/' + ViewActionEnum.ProxyLevel.value + '/' + self.type.lower() + '/'

    @property
    def render_code(self):
        return mark_safe("<a class='inline-link' href='/" + self.__class__.get_model_meta(
            'route', 'route') + '/' + ViewActionEnum.ProxyLevel.value + '/' + self.type.lower() + '/'
                         + ViewActionEnum.Details.value + '/' + str(self.pk) + "/' >" + self.code + "</a>")

    def details_link_config(self, **kwargs):
        return [
        ]

    @classmethod
    def get_serializer(cls):
        CTSerializer = ConfigurableType.get_serializer()

        class GeographySerializer(CTSerializer):
            geography_type = serializers.SerializerMethodField()
            geography_level = serializers.SerializerMethodField()

            def get_geography_type(self, obj):
                from blackwidow.core.models import GeographyLevel
                return GeographyLevel.get_cached_level_by_id(obj.level_id).name

            def get_geography_level(self, obj):
                return obj.level_id

            class Meta:
                model = cls
                fields = [
                    'id', 'code', 'geography_level', 'geography_type',
                    'name', 'parent', 'last_updated'
                ]

        return GeographySerializer
