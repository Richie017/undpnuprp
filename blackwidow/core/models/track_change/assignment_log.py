from django.db import models

from blackwidow.core.generics.views.import_view import get_model
from blackwidow.core.models.contracts.base import DomainEntity
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, save_audit_log, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'Tareq'


@decorate(expose_api('assignment-logs'), save_audit_log, is_object_context,
          route(route='assignment-logs', module=ModuleEnum.Settings, group="Other Admin",
                display_name="Assignment Log"))
class AssignmentLog(DomainEntity):
    model_group = models.CharField(max_length=128, blank=True)
    model_name = models.CharField(max_length=128)
    model_app_label = models.CharField(max_length=128, blank=True)
    relation_name = models.CharField(max_length=128)
    display_name = models.CharField(max_length=128, blank=True)
    object_key = models.IntegerField(default=0)
    current_related_key = models.IntegerField(default=0)
    previous_related_key = models.IntegerField(default=0)

    @property
    def render_model_name(self):
        if self.model_app_label:
            return self.model_app_label + '.' + self.model_name
        return self.model_name

    @property
    def render_object(self):
        self.object = get_model(app_label=self.model_app_label, model_name=self.model_name).objects.filter(
            pk=self.object_key).first()
        if self.object is not None:
            return self.object

    @property
    def model(self):
        return self.model_group

    @property
    def relation(self):
        return self.display_name

    @classmethod
    def default_order_by(cls):
        return ['model_name', 'object_key', '-date_created']

    @classmethod
    def distinct_fields(cls):
        return ['model_name', 'object_key']

    @classmethod
    def table_columns(cls):
        return 'code', 'render_model_name', 'render_object', 'relation_name', 'display_name', \
               'current_related_key', 'previous_related_key', 'date_created'

    @classmethod
    def get_serializer(cls):
        DESerializer = DomainEntity.get_serializer()

        class AssignmentLogSerializer(DESerializer):
            class Meta(DESerializer.Meta):
                model = AssignmentLog
                fields = (
                    'model_name', 'object_key', 'relation', 'previous_related_key', 'current_related_key',
                    'date_created')

        return AssignmentLogSerializer
