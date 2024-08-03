from undp_nuprp.approvals.models import PendingCDCMonthlyReport
from undp_nuprp.reports.config.constants.values import BATCH_SIZE

__author__ = "Ziaul Haque"


class CDCReportManager(object):

    @classmethod
    def generate(cls, batch_count=None, batch_size=BATCH_SIZE):
        cls.handle_calculative_field_calculation()

    @classmethod
    def handle_calculative_field_calculation(cls):
        updatable_monthly_report_objects = PendingCDCMonthlyReport.objects.filter(is_calculative_field_updated=False)
        _count = updatable_monthly_report_objects.count()
        _assigned_codes = ['001001008', '001005005']

        for updatable_entry in updatable_monthly_report_objects:
            PendingCDCMonthlyReport.update_calculated_field_info(
                instance=updatable_entry, assigned_codes=_assigned_codes
            )
        print("Total %d CDC Monthly Report object's updated." % _count)
