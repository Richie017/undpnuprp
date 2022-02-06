from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.models import EligibleBusinessGrantee
from undp_nuprp.approvals.views import GranteeListExportView

__author__ = 'Ziaul Haque'


@decorate(override_view(model=EligibleBusinessGrantee, view=ViewActionEnum.AdvancedExport))
class BusinessGranteeExportView(GranteeListExportView):
    pass
