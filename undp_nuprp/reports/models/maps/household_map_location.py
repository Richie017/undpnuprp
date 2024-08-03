from undp_nuprp.reports.models.base.base import Report

__author__ = 'Ziaul Haque'


# @decorate(is_object_context,
#           route(route='household-map-location', group='Maps', group_order=2, item_order=1, module=ModuleEnum.Reports,
#                 display_name="Household Location"))
class HouseholdLocationReport(Report):
    class Meta:
        proxy = True
