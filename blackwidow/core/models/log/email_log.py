from django.db import models

from blackwidow.core.models.log.base import SystemLog
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'Tareq'


@decorate(is_object_context,
          route(route='email-logs', group='Logs', display_name='Email Log', module=ModuleEnum.Settings))
class EmailLog(SystemLog):
    from blackwidow.core.models.users.user import ConsoleUser

    status = models.CharField(max_length=200, default='')
    recipient_user = models.ForeignKey(ConsoleUser, null=True, default=None, on_delete=models.SET_NULL)

    @classmethod
    def table_columns(cls):
        return 'code', 'status', 'message', 'date_created', 'recipient_user:Recipient'
