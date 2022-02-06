from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.models.base.base import Report

__author__ = 'Kaikobud'


@decorate(is_object_context,
          route(route='violence-against-woman-committee-map', group=' Local Economy Livelihood and Financial Inclusion ',
                item_order=3, group_order=3, module=ModuleEnum.InteractiveMap,
                display_name="Number of Violence Against Woman Committees"))
class ViolenceAgainstWomanCommitteeMapReport(Report):
    class Meta:
        proxy = True
