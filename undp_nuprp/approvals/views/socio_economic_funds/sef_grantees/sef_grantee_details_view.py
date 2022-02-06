from blackwidow.core.generics.views.details_view import GenericDetailsView

from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.models import SEFApprenticeshipGrantee, SEFBusinessGrantee, SEFEducationDropoutGrantee, \
    SEFEducationChildMarriageGrantee, SEFNutritionGrantee

__author__ = 'Ziaul Haque'


class SEFGranteeDetailsView(GenericDetailsView):
    def get_template_names(self):
        return ["sefgrantee/details.html"]


@decorate(override_view(model=SEFApprenticeshipGrantee, view=ViewActionEnum.Details))
class SEFGranteeDetailsView(SEFGranteeDetailsView):
    pass


@decorate(override_view(model=SEFBusinessGrantee, view=ViewActionEnum.Details))
class SEFBusinessGranteeDetailsView(SEFGranteeDetailsView):
    pass


@decorate(override_view(model=SEFEducationDropoutGrantee, view=ViewActionEnum.Details))
class SEFEducationDropoutGranteeDetailsView(SEFGranteeDetailsView):
    pass


@decorate(override_view(model=SEFEducationChildMarriageGrantee, view=ViewActionEnum.Details))
class SEFEducationChildMarriageGranteeDetailsView(SEFGranteeDetailsView):
    pass


@decorate(override_view(model=SEFNutritionGrantee, view=ViewActionEnum.Details))
class SEFNutritionGranteeDetailsView(SEFGranteeDetailsView):
    pass
