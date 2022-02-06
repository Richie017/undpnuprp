from django.conf import settings
from django.urls import reverse

from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from config.model_json_cache import MODEL_JASON_URL
from undp_nuprp.reports.views.base.base_report import GenericReportView

MAPBOX_ACCESS_TOKEN = settings.MAPBOX_ACCESS_TOKEN

__author__ = 'Ziaul Haque'


class GenericInteractiveMapReportView(GenericReportView):
    def get_template_names(self):
        return ['reports/interactive-map.html']

    @staticmethod
    def str_to_list(data):
        """
        Simple function to  convert string to list
        :param data:
        :return: a list(array) generated from data(str)
        """
        try:
            data_list = [int(x) for x in data.split(',')]
            return data_list
        except AttributeError:
            return data

    def get_context_data(self, **kwargs):
        from undp_nuprp.reports.models.interactive_maps.output_one.ward_prioritization_map_report import \
            WardPrioritizationMapReport
        context = super(GenericInteractiveMapReportView, self).get_context_data(**kwargs)
        context['title'] = "Interactive Map Report"
        context['enable_map'] = False
        context['has_second_layer'] = 1  # 1 - True, 0 - False
        context['mapbox_access_token'] = MAPBOX_ACCESS_TOKEN
        context['legend_label'] = "Color Range"
        context['bounding_coords_url'] = '{0}{1}.json?v=1.0.7'.format(MODEL_JASON_URL, 'bounding_coords')
        context['country_geojson_url'] = '{0}{1}.json?v=1.0.7'.format(MODEL_JASON_URL, 'country')
        context['city_geojson_url'] = '{0}{1}.json?v=1.0.7'.format(MODEL_JASON_URL, 'city')
        context['ward_geojson_url'] = '{0}{1}.json?v=1.0.7'.format(MODEL_JASON_URL, 'ward')
        context['mahalla_geojson_url'] = '{0}{1}.json?v=1.0.7'.format(MODEL_JASON_URL, 'mahalla')
        context['poor_settlement_geojson_url'] = '{0}{1}.json?v=1.0.7'.format(MODEL_JASON_URL, 'poor_settlement')
        context["note_url"] = reverse(WardPrioritizationMapReport.get_route_name(ViewActionEnum.Manage))
        return context
