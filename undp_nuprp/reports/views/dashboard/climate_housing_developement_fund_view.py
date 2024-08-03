from crequest.middleware import CrequestMiddleware
from django import forms

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.models.geography.geography import Geography
from blackwidow.core.models.geography.geography_level import GeographyLevel
from blackwidow.engine.decorators.utility import decorate, get_models_with_decorator
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from config.apps import INSTALLED_APPS
from config.model_json_cache import MODEL_JASON_URL
from undp_nuprp.reports.config.climate_housing_development_fund_indicators import \
    climate_housing_development_fund_indicator
from undp_nuprp.reports.models.dashboard.climate_housing_development_fund_report import \
    ClimateHousingDevelopmentFundReport
from undp_nuprp.reports.utils.enums.graph_types import GraphTypeEnum
from undp_nuprp.reports.utils.graph_config.high_chart_configs import get_stacked_column_chart_config, \
    get_column_chart_config, get_bar_chart_config, get_scatter_chart_config, get_pie_chart_config, get_flat_html_config
from undp_nuprp.reports.views.base.base_report import GenericReportView

__author__ = 'Ashraful'


@decorate(override_view(model=ClimateHousingDevelopmentFundReport, view=ViewActionEnum.Manage))
class ClimateHousingDevelopmentFundView(GenericReportView):
    def get(self, request, *args, **kwargs):
        return super(ClimateHousingDevelopmentFundView, self).get(request, *args, **kwargs)

    def get_indicators(self, **kwargs):
        return climate_housing_development_fund_indicator

    def get_context_data(self, **kwargs):
        context = super(ClimateHousingDevelopmentFundView, self).get_context_data(**kwargs)
        context['title'] = "Climate Housing Development Fund"
        context['indicators'] = self.get_indicators(**kwargs)
        return context

    def get_report_parameters(self, **kwargs):
        parameters = super(ClimateHousingDevelopmentFundView, self).get_report_parameters(**kwargs)
        division_level = GeographyLevel.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
            name__icontains='division').first()
        request = CrequestMiddleware.get_request()
        user = request.c_user
        user_role = user.role.name

        filter_roles = get_models_with_decorator(decorator_name='has_data_filter',
                                                 apps=INSTALLED_APPS, include_class=False)
        if user_role in filter_roles:
            json_suffix = '_' + str(user.pk)
        else:
            json_suffix = ''

        parameters['G1'] = self.get_wrapped_parameters((
            {
                'name': 'division',
                'field': GenericModelChoiceField(
                    queryset=Geography.get_role_based_queryset(
                        queryset=Geography.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                            level_id=division_level.pk)),
                    label='Division',
                    empty_label=None,
                    required=False,
                    widget=forms.Select(
                        attrs={
                            'class': 'select2',
                            'width': '220',
                            'multiple': 'multiple',
                            'data-child': 'city_corporation',
                        }
                    )
                )
            },
        ))
        parameters['G2'] = self.get_wrapped_parameters((
            {
                'name': 'city_corporation',
                'field': forms.CharField(
                    label='City Corporation',
                    required=False,
                    widget=forms.TextInput(
                        attrs={
                            'width': '220',
                            'multiple': 'multiple',
                            'class': 'bw-select2',
                            'data-load-none': 'true',
                            'data-depends-on': 'division',
                            'data-depends-property': 'parent',
                            'data-js-url': '{0}{1}{2}.js'.format(MODEL_JASON_URL, Geography.__name__.lower(),
                                                                 json_suffix)
                        }
                    )
                )
            },
        ))

        return parameters

    def get_template_names(self):
        return ['reports/socio-economic-fund/indicators.html']

    def get_json_response(self, content, **kwargs):
        division = self.extract_parameter('division')
        city_corporation = self.extract_parameter('city_corporation')

        indicator = self.extract_parameter('indicator')
        graph_type = self.extract_parameter('type')

        selected_cities = None
        if city_corporation is not None:
            city_ids = [int(id) for id in city_corporation.split(',')]
            selected_cities = Geography.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                level__name__icontains='city').filter(pk__in=city_ids)
        elif division is not None:
            division_ids = [int(id) for id in division.split(',')]
            selected_cities = Geography.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                level__name__icontains='city').filter(
                parent_id__in=division_ids)

        if selected_cities:
            city_ids = selected_cities.values_list('pk', flat=True)
        else:
            city_ids = list()

        report_data = ClimateHousingDevelopmentFundReport().build_report(cities=city_ids,
                                                                         indicator=indicator, graph_type=graph_type)
        extra_params = None
        if isinstance(report_data, tuple):
            extra_params = report_data[1]
            report_data = report_data[0]

        response_dict = {
            'options': self.prepare_graph_meta(indicator=indicator, graph_type=graph_type, params=extra_params),
            'data': report_data
        }

        return super(ClimateHousingDevelopmentFundView, self).get_json_response(
            self.convert_context_to_json(response_dict), **kwargs)

    def prepare_graph_meta(self, indicator, graph_type, params, **kwargs):
        _indicator = [ind for ind in self.get_indicators(**kwargs) if ind['indicator'] == indicator][0]
        # _graph_title = _indicator['full_name']
        if graph_type == GraphTypeEnum.StackedColumnChart.value:
            graph_meta = [gr for gr in _indicator['graph_types'] if gr['type'] == graph_type][0]
            y_axis_title = graph_meta['y_axis_title']
            x_axis_title = graph_meta['x_axis_title']
            point_format = graph_meta['point_format']
            _graph_title = graph_meta['title']
            config = dict()
            if 'config' in graph_meta.keys():
                config.update(**graph_meta['config'])
            return get_stacked_column_chart_config(
                title=_graph_title, y_axis_title=y_axis_title, point_format=point_format, x_axis_title=x_axis_title,
                categories=params, **config)
        if graph_type == GraphTypeEnum.ColumnChart.value:
            graph_meta = [gr for gr in _indicator['graph_types'] if gr['type'] == graph_type][0]
            y_axis_title = graph_meta['y_axis_title']
            x_axis_title = graph_meta['x_axis_title']
            point_format = graph_meta['point_format']
            _graph_title = graph_meta['title']
            return get_column_chart_config(
                title=_graph_title, y_axis_title=y_axis_title, point_format=point_format,
                x_axis_title=x_axis_title, categories=params)
        if graph_type == GraphTypeEnum.HorizontalBarChart.value:
            graph_meta = [gr for gr in _indicator['graph_types'] if gr['type'] == graph_type][0]
            y_axis_title = graph_meta['y_axis_title']
            x_axis_title = graph_meta['x_axis_title']
            point_format = graph_meta['point_format']
            _graph_title = graph_meta['title']
            return get_bar_chart_config(title=_graph_title, y_axis_title=y_axis_title, point_format=point_format,
                                        x_axis_title=x_axis_title, categories=params)
        if graph_type == GraphTypeEnum.ScatterChart.value:
            graph_meta = [gr for gr in _indicator['graph_types'] if gr['type'] == graph_type][0]
            y_axis_title = graph_meta['y_axis_title']
            x_axis_title = graph_meta['x_axis_title']
            decimal_places = graph_meta['decimal_places']
            _graph_title = graph_meta['title']
            return get_scatter_chart_config(
                title=_graph_title, y_axis_title=y_axis_title, decimal_places=decimal_places, x_axis_title=x_axis_title,
                categories=params)
        if graph_type == GraphTypeEnum.PieChart.value:
            graph_meta = [gr for gr in _indicator['graph_types'] if gr['type'] == graph_type][0]
            _graph_title = graph_meta['title']
            point_format = graph_meta['point_format']
            return get_pie_chart_config(title=_graph_title, point_format=point_format)
        if graph_type == GraphTypeEnum.FlatHtml.value:
            return get_flat_html_config()
