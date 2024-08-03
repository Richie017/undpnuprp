from collections import OrderedDict

from blackwidow.core.generics.views.details_view import GenericDetailsView
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.mixins.viewmixin.primary_group_member_view_mixin import PrimaryGroupMemberViewMixin
from undp_nuprp.nuprp_admin.models import PrimaryGroupMember
from undp_nuprp.nuprp_admin.utils.enums.question_type_enum import QuestionTypeEnum
from undp_nuprp.survey.models.response.question_response import QuestionResponse

__author__ = 'Tareq'


@decorate(override_view(model=PrimaryGroupMember, view=ViewActionEnum.Details))
class PrimaryGroupMemberDetailsView(GenericDetailsView, PrimaryGroupMemberViewMixin):
    def get_context_data(self, **kwargs):
        context = super(PrimaryGroupMemberDetailsView, self).get_context_data(**kwargs)
        context['model_meta']['sections'] = self.prepare_survey_data()
        return context


