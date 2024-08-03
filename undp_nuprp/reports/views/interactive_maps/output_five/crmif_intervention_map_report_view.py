from crequest.middleware import CrequestMiddleware
from django import forms
from django.db.models import Sum, F

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.models import GeographyLevel
from blackwidow.core.models.geography.geography import Geography
from blackwidow.engine.decorators.utility import decorate, get_models_with_decorator
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from config.apps import INSTALLED_APPS
from config.model_json_cache import MODEL_JASON_URL
from undp_nuprp.approvals.models import Intervention
from undp_nuprp.reports.models.interactive_maps.output_five.crmif_intervention_map_report import \
    CRMIFInterventionMapReport
from undp_nuprp.reports.views.interactive_maps.output_five.intervention_map_report_view import InterventionMapReportView

__author__ = 'Ziaul Haque'


@decorate(override_view(model=CRMIFInterventionMapReport, view=ViewActionEnum.Manage))
class CRMIFInterventionMapReportView(InterventionMapReportView):

    def get_report_parameters(self, **kwargs):
        request = CrequestMiddleware.get_request()
        parameters = super(CRMIFInterventionMapReportView, self).get_report_parameters(**kwargs)
        user = request.c_user
        user_role = user.role.name

        filter_roles = get_models_with_decorator(
            decorator_name='has_data_filter', apps=INSTALLED_APPS, include_class=False)
        if user_role in filter_roles:
            json_suffix = '_' + str(user.pk)
        else:
            json_suffix = ''

        city_level = GeographyLevel.objects.using(
            BWDatabaseRouter.get_read_database_name()
        ).filter(name__icontains='city').first()

        parameters['G1'] = self.get_wrapped_parameters((
            {
                'name': 'city',
                'field': GenericModelChoiceField(
                    queryset=Geography.get_role_based_queryset(
                        queryset=Geography.objects.using(
                            BWDatabaseRouter.get_read_database_name()
                        ).filter(level_id=city_level.pk)),
                    label='City/Town',
                    empty_label=None,
                    required=False,
                    widget=forms.Select(
                        attrs={
                            'class': 'select2',
                            'width': '220',
                            'multiple': 'multiple',
                            'data-child': 'ward',
                        }
                    )
                )
            },
        ))
        parameters['G2'] = self.get_wrapped_parameters((
            {
                'name': 'ward',
                'field': forms.CharField(
                    label='Ward',
                    required=False,
                    widget=forms.TextInput(
                        attrs={
                            'width': '220',
                            'multiple': 'multiple',
                            'class': 'bw-select2',
                            'data-load-none': 'true',
                            'data-depends-on': 'city',
                            'data-depends-property': 'parent',
                            'data-js-url': '{0}{1}{2}.js'.format(
                                MODEL_JASON_URL, Geography.__name__.lower(), json_suffix)
                        }
                    )
                )
            },
        ))
        return parameters

    def get_context_data(self, **kwargs):
        context = super(CRMIFInterventionMapReportView, self).get_context_data(**kwargs)
        context['title'] = "CRMIF Interventions"

        city_ids = list(Geography.objects.filter(
            level__name='Pourashava/City Corporation'
        ).values_list('id', flat=True))

        context['color_range'] = self.prepare_color_range(city_ids)
        context['total_strategy'] = self.prepare_city_wise_total_data(city_ids)
        context['legend_label'] = "Number of Interventions"
        return context

    @classmethod
    def prepare_color_range(cls, city_ids):
        all_intervention_type = [
            'Embankment cum Road', 'Drain and/or Culvert',
            'Road', 'Multipurpose Use Center'
        ]

        # deal with cdc data
        queryset = Intervention.objects.filter(
            type_of_intervention__in=all_intervention_type,
            crmif__assigned_cdc__address__geography__isnull=False
        ).distinct().values(
            'crmif__assigned_cdc__address__geography_id',
            'crmif__assigned_cdc__address__geography__parent_id'
        ).annotate(Sum('number_of_facilities'))

        city_dict = dict()
        ward_dict = dict()
        for q in queryset:
            ward_dict[q['crmif__assigned_cdc__address__geography_id']] = q['number_of_facilities__sum'] or 0
            if q['crmif__assigned_cdc__address__geography__parent_id'] not in city_dict.keys():
                city_dict[q['crmif__assigned_cdc__address__geography__parent_id']] = 0
            city_dict[q['crmif__assigned_cdc__address__geography__parent_id']] += q['number_of_facilities__sum'] or 0

        # deal with cdc cluster data
        queryset = Intervention.objects.filter(
            type_of_intervention__in=all_intervention_type,
            crmif__assigned_cdc_cluster__address__geography__isnull=False,
            crmif__assigned_cdc__address__geography__isnull=True
        ).distinct().values(
            'crmif__assigned_cdc_cluster__address__geography_id'
        ).annotate(Sum('number_of_facilities'))

        for q in queryset:
            if q['crmif__assigned_cdc_cluster__address__geography_id'] not in city_dict.keys():
                city_dict[q['crmif__assigned_cdc_cluster__address__geography_id']] = 0
            city_dict[q['crmif__assigned_cdc_cluster__address__geography_id']] += q['number_of_facilities__sum'] or 0

        color_dict = dict()
        color_dict['city_range'] = ['> 0', ]
        color_dict['ward_range'] = ['> 0', ]
        for city in city_ids:
            color_dict[city] = 0  # default color range

        if city_dict:
            range_min = [v for k, v in sorted(city_dict.items(), key=lambda item: item[1])][0]
            range_max = [v for k, v in sorted(city_dict.items(), key=lambda item: item[1])][-1]
            range_diff = range_max - range_min
            _range = range_diff // 4
            range1 = range_min + _range
            range2 = range1 + _range
            range3 = range2 + _range

            if range_diff <= 3:
                if range_min != 0:
                    if range_min == 1:
                        color_dict["city_range"] = ['0.01 - ' + str(int(range_min)), ]
                    else:
                        color_dict["city_range"] = ['1 - ' + str(int(range_min)), ]
                for i in range(1, int(range_diff) + 1):
                    color_dict["city_range"] += [
                        str(int(range_min) + (i - 1)) + ".01" + ' - ' + str(int(range_min) + i), ]
                for q, v in city_dict.items():
                    city_id = q
                    count = v or 0
                    
                    if count == 0:
                        continue
                    elif count <= range_min:
                        color_dict[city_id] = 1
                    elif range_min < count <= range_min + 1:
                        color_dict[city_id] = 2
                    elif range_min + 1 < count <= range_min + 2:
                        color_dict[city_id] = 3
                    else:
                        color_dict[city_id] = 4
            else:
                color_dict["city_range"] = [
                    '1 - ' + str(range1),
                    str(range1 + 1) + ' - ' + str(range2),
                    str(range2 + 1) + ' - ' + str(range3),
                    '> ' + str(range3),
                ]

                for q, v in city_dict.items():
                    city_id = q
                    count = v or 0
                    
                    if count == 0:
                        continue
                    elif count <= range1:
                        color_dict[city_id] = 1
                    elif range1 < count <= range2:
                        color_dict[city_id] = 2
                    elif range2 < count <= range3:
                        color_dict[city_id] = 3
                    else:
                        color_dict[city_id] = 4

        ward_queryset = Geography.objects.filter(level__name='Ward', parent_id__in=city_ids).values('id')
        for ward in ward_queryset:
            color_dict[ward['id']] = 0  # default color range

        if ward_dict:
            range_min = [v for k, v in sorted(ward_dict.items(), key=lambda item: item[1])][0]
            range_max = [v for k, v in sorted(ward_dict.items(), key=lambda item: item[1])][-1]
            range_diff = range_max - range_min
            _range = range_diff // 4
            range1 = range_min + _range
            range2 = range1 + _range
            range3 = range2 + _range

            if range_diff <= 3:
                if range_min != 0:
                    if range_min == 1:
                        color_dict["ward_range"] = ['0.01 - ' + str(int(range_min)), ]
                    else:
                        color_dict["ward_range"] = ['1 - ' + str(int(range_min)), ]
                for i in range(1, int(range_diff) + 1):
                    color_dict["ward_range"] += [
                        str(int(range_min) + (i - 1)) + ".01" + ' - ' + str(int(range_min) + i), ]
                for q, v in ward_dict.items():
                    ward_id = q
                    count = v or 0
                    
                    if count == 0:
                        continue
                    elif count <= range_min:
                        color_dict[ward_id] = 1
                    elif range_min < count <= range_min + 1:
                        color_dict[ward_id] = 2
                    elif range_min + 1 < count <= range_min + 2:
                        color_dict[ward_id] = 3
                    else:
                        color_dict[ward_id] = 4
            else:
                color_dict["ward_range"] = [
                    '1 - ' + str(range1),
                    str(range1 + 1) + ' - ' + str(range2),
                    str(range2 + 1) + ' - ' + str(range3),
                    '> ' + str(range3),
                ]

                for q, v in ward_dict.items():
                    ward_id = q
                    count = v or 0
                    
                    if count == 0:
                        continue
                    elif count <= range1:
                        color_dict[ward_id] = 1
                    elif range1 < count <= range2:
                        color_dict[ward_id] = 2
                    elif range2 < count <= range3:
                        color_dict[ward_id] = 3
                    else:
                        color_dict[ward_id] = 4

        return color_dict

    @classmethod
    def prepare_city_wise_total_data(cls, city_ids):
        all_intervention_type = [
            'Embankment cum Road', 'Drain and/or Culvert',
            'Road', 'Multipurpose Use Center'
        ]

        # deal with cdc
        queryset = Intervention.objects.filter(
            type_of_intervention__in=all_intervention_type,
            crmif__assigned_cdc__address__geography__isnull=False
        ).distinct().values(
            'crmif__assigned_cdc__address__geography__parent_id'
        ).annotate(Sum('number_of_facilities'))

        total_key = 'Interventions'
        result = dict()
        for city in city_ids:
            result[city] = {
                total_key: 0
            }

        for _item in queryset:
            result[
                _item['crmif__assigned_cdc__address__geography__parent_id']
            ][total_key] = _item['number_of_facilities__sum'] or 0

        # deal with cdc cluster
        queryset = Intervention.objects.filter(
            type_of_intervention__in=all_intervention_type,
            crmif__assigned_cdc_cluster__address__geography__isnull=False,
            crmif__assigned_cdc__address__geography__isnull=True
        ).distinct().values(
            'crmif__assigned_cdc_cluster__address__geography_id'
        ).annotate(Sum(F('number_of_facilities')))

        for _item in queryset:
            result[
                _item['crmif__assigned_cdc_cluster__address__geography_id']
            ][total_key] += _item['number_of_facilities__sum'] or 0

        return result

    @classmethod
    def prepare_intervention_data(cls, ward_ids=None, city_ids=None):
        embankment = 'Embankment cum Road'
        drain = 'Drain and/or Culvert'
        road = 'Road'
        multipurpose_use_center = 'Multipurpose Use Center'

        all_intervention_type = [
            'Embankment cum Road', 'Drain and/or Culvert',
            'Road', 'Multipurpose Use Center'
        ]
        intervention_type_dict = {
            'Length of Embankment cum Road (in meters)': embankment,
            'Length of Road (in meters)': road,
            'Length of Drain (in meters)': drain,
            'Number of Multipurpose Use Center': multipurpose_use_center
        }

        annotation_dict = {
            'Length of Embankment cum Road (in meters)': 'length',
            'Length of Road (in meters)': 'length',
            'Length of Drain (in meters)': 'length',
            'Number of Multipurpose Use Center': 'number_of_facilities',
        }

        # prepare data for cdc
        queryset = Intervention.objects.filter(
            type_of_intervention__in=all_intervention_type,
            crmif__assigned_cdc__address__geography__isnull=False
        ).distinct()
        if ward_ids:
            queryset = queryset.filter(crmif__assigned_cdc__address__geography_id__in=ward_ids)
            geography_ids = ward_ids + city_ids
        elif city_ids:
            queryset = queryset.filter(crmif__assigned_cdc__address__geography__parent_id__in=city_ids)
            geography_ids = city_ids + list(Geography.objects.filter(
                level__name='Ward', parent__in=city_ids
            ).values_list('pk', flat=True))
        else:
            geography_ids = list(Geography.objects.filter(
                level__name__in=['Pourashava/City Corporation', 'Ward']
            ).values_list('pk', flat=True))

        result = dict()
        for geography_id in geography_ids:
            result[geography_id] = {
                'Length of Embankment cum Road (in meters)': 0,
                'Length of Road (in meters)': 0,
                'Length of Drain (in meters)': 0,
                'Number of Multipurpose Use Center': 0
            }

        for _key, _type in intervention_type_dict.items():
            _annotator = annotation_dict[_key]
            _queryset = queryset.filter(
                type_of_intervention=_type
            ).values(
                'crmif__assigned_cdc__address__geography_id',
                'crmif__assigned_cdc__address__geography__parent_id'
            ).annotate(Sum(F(_annotator)))

            for _item in _queryset:
                total_facilities = _item['{}__sum'.format(_annotator)] or 0
                result[_item['crmif__assigned_cdc__address__geography_id']][_key] = total_facilities
                result[_item['crmif__assigned_cdc__address__geography__parent_id']][_key] += total_facilities

        # prepare data for cdc cluster
        queryset = Intervention.objects.filter(
            type_of_intervention__in=all_intervention_type,
            crmif__assigned_cdc_cluster__address__geography__isnull=False,
            crmif__assigned_cdc__address__geography__isnull=True
        ).distinct()

        if city_ids:
            queryset = queryset.filter(crmif__assigned_cdc_cluster__address__geography_id__in=city_ids)

        for _key, _types in intervention_type_dict.items():
            _annotator = annotation_dict[_key]
            _queryset = queryset.filter(
                type_of_intervention=_types
            ).values(
                'crmif__assigned_cdc_cluster__address__geography_id'
            ).annotate(Sum(F(_annotator)))

            for _item in _queryset:
                total_facilities = _item['{}__sum'.format(_annotator)] or 0
                result[_item['crmif__assigned_cdc_cluster__address__geography_id']][_key] += total_facilities

        return result

    def get_json_response(self, content, **kwargs):
        city_ids = self.str_to_list(self.extract_parameter('city'))
        ward_ids = self.str_to_list(self.extract_parameter('ward'))

        data_dict = dict()
        data_dict['title'] = "CRMIF Interventions Location Map"
        data_dict['data'] = self.prepare_intervention_data(ward_ids, city_ids)
        data_dict['location_data'] = self.prepare_intervention_location_data(report_type="CRMIF", city_ids=city_ids)

        return super(CRMIFInterventionMapReportView, self).get_json_response(
            self.convert_context_to_json(data_dict), **kwargs)
