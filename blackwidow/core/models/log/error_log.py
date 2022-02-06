from django.db import models

from blackwidow.core.models.log.base import SystemLog
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'Tareq'


@decorate(is_object_context,
          route(route='system-logs', group='Logs', display_name='Error Log', module=ModuleEnum.Settings))
class ErrorLog(SystemLog):
    error_code = models.CharField(max_length=512, default='')
    stacktrace = models.TextField(null=True)

    @classmethod
    def table_columns(cls):
        return 'code', 'message', 'created_by', 'date_created'

    @property
    def details_config(self):
        dic = super().details_config
        dic['Created By'] = self.created_by if self.created_by else "N/A"
        return dic
