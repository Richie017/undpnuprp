from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.reports.config.economic_development_and_livelihood_indicators import \
    economic_development_and_livelihood_indicators
from undp_nuprp.reports.models.dashboard.economic_development_and_livelihoods import EconomicDevelopmentAndLivelihood
from undp_nuprp.reports.views import GenericReportView


@decorate(override_view(model=EconomicDevelopmentAndLivelihood, view=ViewActionEnum.Manage))
class EconomicDevelopmentAndLivelihoodView(GenericReportView):
    def get(self, request, *args, **kwargs):
        return super(EconomicDevelopmentAndLivelihoodView, self).get(request, *args, **kwargs)

    def get_indicators(self, **kwargs):
        return economic_development_and_livelihood_indicators

    def get_context_data(self, **kwargs):
        context = super(EconomicDevelopmentAndLivelihoodView, self).get_context_data(**kwargs)
        context['title'] = "Gender"
        context['indicators'] = self.get_indicators(**kwargs)
        return context

    def get_template_names(self):
        return ['reports/socio-economic-fund/indicators.html']

    def get_json_response(self, content, **kwargs):
        indicator = self.extract_parameter('indicator')
        graph_type = self.extract_parameter('type')

        report_data = EconomicDevelopmentAndLivelihood().build_report(indicator=indicator, graph_type=graph_type)

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

        return super(EconomicDevelopmentAndLivelihoodView, self).get_json_response(
            self.convert_context_to_json(response_dict), **kwargs
        )
