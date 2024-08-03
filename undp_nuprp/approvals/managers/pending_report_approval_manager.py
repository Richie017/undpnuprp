from undp_nuprp.approvals.models import PendingCDCMonthlyReport, PendingSCGMonthlyReport


class PendingReportApprovalManager(object):
    @classmethod
    def approve_cdc_reports(cls, *args, **kwargs):
        for pending_cdc_report in PendingCDCMonthlyReport.objects.all():
            pending_cdc_report.approve_to(*args, **kwargs)

    @classmethod
    def approve_scg_reports(cls, *args, **kwargs):
        for pending_scg_report in PendingSCGMonthlyReport.objects.all():
            pending_scg_report.approve_to(*args, **kwargs)
