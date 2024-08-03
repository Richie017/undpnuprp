from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.reports.config.savings_and_credit_indicators import savings_and_credit_indicator
from undp_nuprp.reports.models import SavingsAndCreditReport
from undp_nuprp.reports.utils.enums.graph_types import GraphTypeEnum
from undp_nuprp.reports.utils.graph_config.high_chart_configs import get_stacked_column_chart_config, \
    get_column_chart_config, get_pie_chart_config, get_flat_html_config

from undp_nuprp.reports.views.base.base_report import GenericReportView

__author__ = 'Ashraful'


@decorate(override_view(model=SavingsAndCreditReport, view=ViewActionEnum.Manage))
class SavingsAndCreditView(GenericReportView):
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_indicators(self, **kwargs):
        return savings_and_credit_indicator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Savings and Credit"
        context['indicators'] = self.get_indicators(**kwargs)
        return context

    def get_report_parameters(self, **kwargs):
        parameters = super().get_report_parameters(**kwargs)
        return parameters

    def get_template_names(self):
        return ['reports/socio-economic-fund/plain-indicators.html']

    def get_json_response(self, content, **kwargs):
        indicator = self.extract_parameter('indicator')
        graph_type = self.extract_parameter('type')

        report_data = SavingsAndCreditReport().build_report(indicator=indicator, graph_type=graph_type)

        extra_params = None
        if isinstance(report_data, tuple):
            extra_params = report_data[1]
            report_data = report_data[0]

        if isinstance(report_data, tuple):
            report_data = report_data[0]

        response_dict = {
            'options': self.prepare_graph_meta(indicator=indicator, graph_type=graph_type, params=extra_params),
            'data': report_data
        }

        return super().get_json_response(self.convert_context_to_json(response_dict), **kwargs)

    def prepare_graph_meta(self, indicator, graph_type, params, **kwargs):
        _indicator = [ind for ind in self.get_indicators(**kwargs) if ind['indicator'] == indicator][0]
        if graph_type == GraphTypeEnum.StackedColumnChart.value:
            graph_meta = [gr for gr in _indicator['graph_types'] if gr['type'] == graph_type][0]
            y_axis_title = graph_meta['y_axis_title']
            x_axis_title = graph_meta['x_axis_title']
            point_format = graph_meta['point_format']

            _graph_title = '<div class="ttip">{} <p class="tooltiptext">{}</p></div>'.format(
                graph_meta['title'], graph_meta['definition']) if 'definition' in graph_meta.keys() else graph_meta[
                'title']
            _graph_export_title = graph_meta['title']
            config = dict()
            if 'config' in graph_meta.keys():
                config.update(**graph_meta['config'])
            return get_stacked_column_chart_config(
                title=_graph_title, export_title=_graph_export_title, y_axis_title=y_axis_title,
                point_format=point_format, x_axis_title=x_axis_title, categories=params, **config)
        if graph_type == GraphTypeEnum.ColumnChart.value:
            graph_meta = [gr for gr in _indicator['graph_types'] if gr['type'] == graph_type][0]
            y_axis_title = graph_meta['y_axis_title']
            x_axis_title = graph_meta['x_axis_title']
            point_format = graph_meta['point_format']
            _graph_title = graph_meta['title']
            return get_column_chart_config(
                title=_graph_title, y_axis_title=y_axis_title, point_format=point_format,
                x_axis_title=x_axis_title, categories=params)
        if graph_type == GraphTypeEnum.PieChart.value:
            graph_meta = [gr for gr in _indicator['graph_types'] if gr['type'] == graph_type][0]
            _graph_title = '<div class="ttip">{} <p class="tooltiptext">{}</p></div>'.format(
                graph_meta['title'], graph_meta['definition']) if 'definition' in graph_meta.keys() else graph_meta[
                'title']
            point_format = graph_meta['point_format']
            _graph_export_title = graph_meta['title']
            return get_pie_chart_config(title=_graph_title, export_title=_graph_export_title, point_format=point_format)
        if graph_type == GraphTypeEnum.FlatHtml.value:
            return get_flat_html_config()
