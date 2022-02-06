from django.conf import settings
from django.utils.safestring import mark_safe

from undp_nuprp.approvals.models.interactive_maps.output_five.sif_and_crmif_intervention import SIFAndCRMIFIntervention
from undp_nuprp.reports.views.interactive_maps.interactive_map_report import GenericInteractiveMapReportView

__author__ = 'Ziaul Haque'


class InterventionMapReportView(GenericInteractiveMapReportView):
    def get_template_names(self):
        return ['reports/interactive-map-sif-crmif.html']

    @classmethod
    def get_image_url(cls, image_file):
        if not settings.S3_STATIC_ENABLED:
            return "/{0}".format(image_file)
        return "{0}{1}{2}".format(settings.S3_BASE_URL, settings.MEDIA_DIRECTORY, image_file)

    @staticmethod
    def get_location(latitude, longitude):
        return mark_safe('<a class="inline-link" href="http://maps.google.com/maps?z=17&q='
                         + str(latitude) + ','
                         + str(longitude) + '" target="_blank">'
                         + str(latitude) + ', ' + str(longitude) + '</a>')

    def get_context_data(self, **kwargs):
        ctx_ = super(InterventionMapReportView, self).get_context_data(**kwargs)
        ctx_["marker_info"] = self.get_mapped_marker()
        ctx_['legend_label'] = "Color Range"
        return ctx_

    @staticmethod
    def get_mapped_marker():
        return {
            "Footpath": "footpath.svg",
            "Drain and/or Culvert": "drain.svg",
            "Solar Street Light": "street_light.svg",
            "Non-Solar Street Light": "street_light.svg",
            "Deep Tubewell": "water.svg",
            "Deep Tubewell with submersible pump": "water.svg",
            "Bathroom": "bathroom.svg",
            "Twin Pit Latrine": "toilet.svg",
            "Single Pit Latrine": "toilet.svg",
            "Septic Tank": "toilet.svg",
            "Community Latrine": "toilet.svg",
            "Multipurpose Use Center": "multiple_house.svg",
            "Road": "road.svg",
            "Embankment cum Road": "road.svg"
        }

    @classmethod
    def get_marker_icon(cls, intervention_type):
        marker_mapping = cls.get_mapped_marker()
        if intervention_type in marker_mapping.keys():
            return marker_mapping[intervention_type]
        return "blue1.svg"

    @classmethod
    def prepare_intervention_location_data(cls, report_type, city_ids=None):
        queryset = SIFAndCRMIFIntervention.objects.filter(type_of_report=report_type)
        if city_ids:
            queryset = queryset.filter(city_id__in=city_ids)

        queryset = queryset.values(
            'image__file', 'location__latitude', 'location__longitude', 'survey_time',
            'type_of_intervention', 'footpath_length', 'drain_length', 'number_of_benefited_households'
        )
        locations = []
        for q in queryset:
            _item = {
                'marker_icon': cls.get_marker_icon(q['type_of_intervention']),
                'intervention_type': q['type_of_intervention'],
                'latitude': q['location__latitude'],
                'longitude': q['location__longitude'],
                'location': cls.get_location(q['location__latitude'], q['location__longitude']),
                'survey_time': q['survey_time'].strftime("%d/%m/%Y") if q['survey_time'] else 'N/A',
                'image_url': cls.get_image_url(q['image__file']) if q['image__file'] else None,
                'footpath_length': q['footpath_length'] if q['footpath_length'] else 'N/A',
                'drain_length': q['drain_length'] if q['drain_length'] else 'N/A',
                'number_of_benefited_households': q['number_of_benefited_households'] if q[
                    'number_of_benefited_households'] else 'N/A',
            }
            locations.append(_item)

        return locations
