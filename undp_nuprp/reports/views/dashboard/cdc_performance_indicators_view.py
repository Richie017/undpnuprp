"""
    Created by tareq on 3/13/17
"""

from django import forms
from datetime import date

from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.reports.config.cdc_performance_indicators import cdc_performance_indicators
from undp_nuprp.reports.models.dashboard.cdc_performance_report import CDCPerformanceReport
from undp_nuprp.reports.views.base.base_report import GenericReportView

__author__ = 'Tareq, Kaikobud'


@decorate(override_view(model=CDCPerformanceReport, view=ViewActionEnum.Manage))
class CDCPerformanceReportView(GenericReportView):
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_indicators(self, **kwargs):
        return cdc_performance_indicators

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "CDC Performance"
        context['indicators'] = self.get_indicators(**kwargs)
        return context

    def get_report_parameters(self):
        parameters = super(CDCPerformanceReportView, self).get_report_parameters()
        today = date.today()
        year_choices = tuple()
        for y in range(2000, 2100):
            year_choices += ((y, str(y)),)
        parameters['G1'] = self.get_wrapped_parameters((
            {
                'name': 'year',
                'field': forms.ChoiceField(
                    choices=year_choices,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    ), initial=today.year
                )
            },
        ))
        return parameters

    def get_template_names(self):
        return ['reports/cdc-performance/indicators.html']

    def get_json_response(self, content, **kwargs):
        year = self.extract_parameter('year')
        graph_type = self.extract_parameter('type')

        report_data = CDCPerformanceReport().build_report(graph_type=graph_type, year=year)

        if isinstance(report_data, tuple):
            report_data = report_data[0]

        response_dict = {
            'data': report_data
        }

        return super(CDCPerformanceReportView, self).get_json_response(
            self.convert_context_to_json(response_dict), **kwargs
        )