from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.models.grantees.short_listed_eligible_grantees.shortlisted_eligible_education_early_marriage_grantee import \
    ShortListedEligibleEducationEarlyMarriageGrantee
from undp_nuprp.approvals.views import GranteeListExportView

__author__ = 'Shuvro'


@decorate(override_view(model=ShortListedEligibleEducationEarlyMarriageGrantee, view=ViewActionEnum.AdvancedExport))
class ShortListedEducationEarlyMarriageGranteeExportView(GranteeListExportView):
    pass
