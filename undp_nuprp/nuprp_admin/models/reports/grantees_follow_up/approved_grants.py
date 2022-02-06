from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.nuprp_admin.models.reports.grantees_follow_up.grantee_follow_up import GranteeFollowUp

__author__ = "Shama"


@decorate(is_object_context,
          route(route='approved-grants', group='Grants', module=ModuleEnum.Execute,
                display_name='Approved Grants', group_order=2, item_order=4))
class ApprovedGrants(GranteeFollowUp):
    class Meta:
        app_label = 'nuprp_admin'
