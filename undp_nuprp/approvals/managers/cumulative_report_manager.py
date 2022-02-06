from undp_nuprp.approvals.models import CumulativeReport

__author__ = 'Ziaul Haque'


class CumulativeReportManager(object):
    @classmethod
    def generate_reports(cls, *args, **kwargs):
        CumulativeReport.generate_cumulative_report()
