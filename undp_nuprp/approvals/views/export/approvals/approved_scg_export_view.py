from blackwidow.core.generics.views.advanced_export_view import AdvancedGenericExportView
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.models.savings_and_credits.scg_reports.approved_scg_monthly_report import \
    ApprovedSCGMonthlyReport


@decorate(override_view(model=ApprovedSCGMonthlyReport, view=ViewActionEnum.AdvancedExport))
class ApprovedSCGExportView(AdvancedGenericExportView):
    def get_template_names(self):
        return ['shared/display-templates/approvedscgmonthlyreport/_advanced_export_form.html']
