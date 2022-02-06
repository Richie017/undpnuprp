from django.conf import settings

from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.models.base.base import Report

EXPORT_FILE_ROOT = settings.EXPORT_FILE_ROOT
STATIC_EXPORT_URL = settings.STATIC_EXPORT_URL
S3_STATIC_ENABLED = settings.S3_STATIC_ENABLED

__author__ = 'Ziaul Haque'


@decorate(is_object_context,
          route(route='dynamic-survey-data-exporter', group='Dynamic Survey', group_order=6,
                module=ModuleEnum.Administration,
                display_name="Dynamic Survey Export File Generator", item_order=4))
class DynamicSurveyDataExporter(Report):
    class Meta:
        proxy = True
        app_label = 'survey'
