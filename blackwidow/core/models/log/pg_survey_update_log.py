from django.db import models
from blackwidow.core.models.log.base import SystemLog
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'Shuvro'


@decorate(is_object_context,
          route(route='pg-survey-update-logs', group='Logs', display_name='PG Survey Update Log',
                module=ModuleEnum.Settings))
class PGSurveyUpdateLog(SystemLog):
    survey_response = models.ForeignKey('survey.SurveyResponse', null=True, on_delete=models.SET_NULL)
    requested_time = models.BigIntegerField(default=0)
    completion_time = models.BigIntegerField(default=0)
    status = models.CharField(max_length=200, null=True, default='')

    @property
    def render_requested_time(self):
        if self.requested_time:
            return self.render_timestamp(self.requested_time)
        return 'N/A'

    @property
    def render_completion_time(self):
        if self.completion_time:
            return self.render_timestamp(self.completion_time)
        return 'N/A'

    @classmethod
    def get_datetime_fields(cls):
        return ['requested_time', 'completion_time']

    @classmethod
    def table_columns(cls):
        return 'code', 'survey_response', 'render_requested_time', 'render_completion_time', 'status', 'created_by'
