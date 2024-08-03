from blackwidow.core.generics.views.advanced_export_view import AdvancedGenericExportView
from blackwidow.core.models import Organization
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

from undp_nuprp.approvals.models import PMFReport

__author__ = 'Ziaul Haque'


@decorate(override_view(model=PMFReport, view=ViewActionEnum.AdvancedExport))
class PMFReportExportView(AdvancedGenericExportView):

    def start_background_worker(self, request, organization, export_file_name, *args, **kwargs):
        if not organization:
            organization = Organization.objects.first()
        filename, path = PMFReport.export_to_excel(
            organization=organization,
            user=request.c_user,
            filename=export_file_name,
            query_params=self.refine_parameters(request),
            **kwargs
        )
