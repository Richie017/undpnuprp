from blackwidow.core.generics.views.printable_views.printable_details_view import GenericPrintableContentView
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.mixins.viewmixin.primary_group_member_view_mixin import PrimaryGroupMemberViewMixin
from undp_nuprp.nuprp_admin.models import PrimaryGroupMember


@decorate(override_view(model=PrimaryGroupMember, view=ViewActionEnum.Print))
class PrimaryGroupMemberPrintView(GenericPrintableContentView, PrimaryGroupMemberViewMixin):

    def get_context_data(self, **kwargs):
        context = super(PrimaryGroupMemberPrintView, self).get_context_data(**kwargs)
        context['model_meta']['sections'] = self.prepare_survey_data()
        return context

    def get_template_names(self):
        return ['shared/pg_member_printable_info/pg_member_printable_info.html']

