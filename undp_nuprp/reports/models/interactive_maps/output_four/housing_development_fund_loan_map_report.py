from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.reports.models.base.base import Report

__author__ = 'Ziaul Haque'


@decorate(is_object_context,
          route(route='housing-development-fund-loan-map', group=' Housing Finance ',
                item_order=1, group_order=4, module=ModuleEnum.InteractiveMap,
                display_name="Number of Households Received Housing Loan from CHDF"))
class CHDFLoanMapReport(Report):
    class Meta:
        proxy = True
