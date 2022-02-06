from django.db import models

from blackwidow.core.models.contracts.base import DomainEntity
from blackwidow.core.models.log.audit_log import AuditLog
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'Tareq'


@decorate(is_object_context, route(route='activation-logs', group='Logs', display_name='Activation Log',
          module=ModuleEnum.Settings, group_order=3, item_order=1))
class ActivationLog(AuditLog):
    display_name = models.CharField(max_length=128, default='Unspecified')
    action = models.CharField(max_length=128, default='Unspecified')

    @classmethod
    def get_object_inline_buttons(cls):
        return []

    def details_link_config(self, **kwargs):
        return []

    @classmethod
    def get_manage_buttons(cls):
        return []

    @property
    def render_activation_action(self):
        return self.action

    @classmethod
    def table_columns(cls):
        return ('render_code', 'model_name', 'display_name', 'render_activation_action', 'created_by:Action By',
                'last_updated:Action Time')

    @classmethod
    def log(cls, model=DomainEntity, name='Unspecified', action='Unspecified'):
        try:
            _log = cls()
            _log.model_name = model.get_audit_log_model_name()
            _log.model_pk = model.pk
            _log.display_name = name
            _log.action = action
            _log.save()
        except Exception as exp:
            ErrorLog.log(exp=exp)
