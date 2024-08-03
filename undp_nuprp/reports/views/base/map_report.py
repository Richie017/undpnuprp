from undp_nuprp.reports.views.base.base_report import GenericReportView

__author__ = 'Tareq'


class GenericMapReportView(GenericReportView):
    def get_template_names(self):
        return ['reports/map-report-view.html']
