from django.db import models

from blackwidow.core.models.log.base import SystemLog
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'Tareq'


@decorate(is_object_context,
          route(route='scheduler-logs', group='Logs', display_name='Scheduler Log', module=ModuleEnum.Settings))
class SchedulerLog(SystemLog):
    status = models.CharField(max_length=200, default='')
    reference_task = models.CharField(max_length=256, blank=True)
    scheduled_time = models.BigIntegerField(default=0)
    start_time = models.BigIntegerField(default=0)
    end_time = models.BigIntegerField(default=0)

    @property
    def render_start_time(self):
        if self.start_time:
            return self.render_timestamp(self.start_time)
        return 'N/A'

    @property
    def render_end_time(self):
        if self.end_time:
            return self.render_timestamp(self.end_time)
        return 'N/A'

    @property
    def render_run_time(self):
        if self.end_time and self.start_time:
            return str((self.end_time - self.start_time) / 1000) + ' second(s)'
        return 'N/A'

    @classmethod
    def table_columns(cls):
        return 'code', 'reference_task', 'render_start_time', 'render_end_time', 'render_run_time', 'status', \
               'created_by', 'date_created'
