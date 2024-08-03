"""
Created by tareq on 3/7/17
"""

from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.models.base.base import Report

__author__ = 'Tareq'


@decorate(
    is_object_context,
    route(
        route='survey-location-map',
        group='Maps', item_order=3,
        group_order=11,
        module=ModuleEnum.Reports,
        display_name="HH Survey Location"
    )
)
class SurveyLocationReport(Report):
    class Meta:
        proxy = True
