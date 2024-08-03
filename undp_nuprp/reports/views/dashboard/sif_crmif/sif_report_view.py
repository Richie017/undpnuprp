from blackwidow.core.models.geography.geography import Geography
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.clock import Clock
from undp_nuprp.reports.config.sif_indicator import sif_indicator
from undp_nuprp.reports.models.dashboard.sif_report import SIFReport
from undp_nuprp.reports.views.dashboard.sif_crmif.base_sif_crmif_report_view import BaseSIFCRMIFReportView

__author__ = 'Shuvro'


@decorate(override_view(model=SIFReport, view=ViewActionEnum.Manage))
class SIFReportView(BaseSIFCRMIFReportView):
    def get_indicators(self, **kwargs):
        return sif_indicator

    def get_context_data(self, **kwargs):
        context = super(BaseSIFCRMIFReportView, self).get_context_data(**kwargs)
        context['title'] = "SIF"
        context['indicators'] = self.get_indicators(**kwargs)
        return context

    def get_json_response(self, content, **kwargs):
        date_range = self.extract_parameter('date_range')

        division = self.extract_parameter('division')
        city_corporation = self.extract_parameter('city_corporation')
        ward = self.extract_parameter('ward')

        indicator = self.extract_parameter('indicator')
        graph_type = self.extract_parameter('type')

        selected_wards = None
        if ward is not None:
            ward_ids = [int(id) for id in ward.split(',')]
            selected_wards = Geography.objects.filter(
                level__name__icontains='ward').filter(pk__in=ward_ids)
        elif city_corporation is not None:
            city_ids = [int(id) for id in city_corporation.split(',')]
            selected_wards = Geography.objects.filter(
                level__name__icontains='ward').filter(parent_id__in=city_ids)
        elif division is not None:
            division_ids = [int(id) for id in division.split(',')]
            selected_wards = Geography.objects.filter(
                level__name__icontains='ward').filter(
                parent__parent_id__in=division_ids)

        if selected_wards:
            ward_ids = selected_wards.values_list('pk', flat=True)
        else:
            ward_ids = list()

        f_date, t_date = Clock.date_range_from_str(date_range)

        report_data = SIFReport().build_report(from_time=f_date, to_time=t_date, wards=ward_ids,
                                                                     indicator=indicator, graph_type=graph_type)
        extra_params = None
        if isinstance(report_data, tuple):
            extra_params = report_data[1]
            report_data = report_data[0]

        response_dict = {
            'options': self.prepare_graph_meta(indicator=indicator, graph_type=graph_type, params=extra_params),
            'data': report_data
        }

        return super(BaseSIFCRMIFReportView, self).get_json_response(self.convert_context_to_json(response_dict),
                                                                            **kwargs)