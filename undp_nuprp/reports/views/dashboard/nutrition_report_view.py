from datetime import date
from django import forms

from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.utils.month_enum import MonthEnum
from undp_nuprp.reports.config.nutrition_indicator import nutrition_indicators
from undp_nuprp.reports.models.dashboard.nutrition_report import NutritionReport
from undp_nuprp.reports.views import GenericReportView


@decorate(override_view(model=NutritionReport, view=ViewActionEnum.Manage))
class NutritionReportView(GenericReportView):
    def get(self, request, *args, **kwargs):
        return super(NutritionReportView, self).get(request, *args, **kwargs)

    def get_indicators(self, **kwargs):
        return nutrition_indicators

    def get_context_data(self, **kwargs):
        context = super(NutritionReportView, self).get_context_data(**kwargs)
        context['title'] = "Nutrition"
        context['indicators'] = self.get_indicators(**kwargs)
        return context

    def get_report_parameters(self):
        parameters = super(NutritionReportView, self).get_report_parameters()
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
        parameters['G2'] = self.get_wrapped_parameters((
            {
                'name': 'month',
                'field': forms.ChoiceField(
                    choices=MonthEnum.get_choices(),
                    initial=today.month,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    )
                )
            },
        ))
        return parameters

    def get_template_names(self):
        return ['reports/nutrition/indicators.html']

    def get_json_response(self, content, **kwargs):
        indicator = self.extract_parameter('indicator')
        graph_type = self.extract_parameter('type')
        year = self.extract_parameter('year')
        month = self.extract_parameter('month')

        report_data = NutritionReport().build_report(indicator=indicator, graph_type=graph_type, year=year, month=month)

        # extra_params = None
        # if isinstance(report_data, tuple):
        #     extra_params = report_data[1]
        #     report_data = report_data[0]

        if isinstance(report_data, tuple):
            report_data = report_data[0]

        response_dict = {
            # 'options': self.prepare_graph_meta(indicator=indicator, graph_type=graph_type, params=extra_params),
            'data': report_data
        }

        return super(NutritionReportView, self).get_json_response(
            self.convert_context_to_json(response_dict), **kwargs
        )
