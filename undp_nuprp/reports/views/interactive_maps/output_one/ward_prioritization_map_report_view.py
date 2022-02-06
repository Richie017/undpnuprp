from django import forms
from django.db.models import Sum, F

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.models import Geography, GeographyLevel
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.approvals.models import Intervention
from undp_nuprp.reports.models import SEFGranteesInfoCache
from undp_nuprp.reports.models.interactive_maps.output_one.ward_prioritization_map_report import \
    WardPrioritizationMapReport
from undp_nuprp.reports.views.interactive_maps.interactive_map_report import GenericInteractiveMapReportView

__author__ = 'Kaikobud'

indicator_choices = (
    # ('', 'Select One'),
    ('Poverty Index', 'Poverty Index'),
    ('Infrastructure Index', 'Infrastructure Index'),
    ('Livelihood Index', 'Livelihood Index'),
    ('Land Tenure and Housing Index', 'Land Tenure and Housing Index'),
    ('Total Population', 'Total Population')
)


@decorate(override_view(model=WardPrioritizationMapReport, view=ViewActionEnum.Manage))
class WardPrioritizationMapReportView(GenericInteractiveMapReportView):
    def get_template_names(self):
        return ['reports/interactive-map-ward-prioritization.html']

    def get_report_parameters(self, **kwargs):
        parameters = super(WardPrioritizationMapReportView, self).get_report_parameters(**kwargs)

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
                    empty_label='Select One',
                    required=False,
                    widget=forms.Select(
                        attrs={
                            'class': 'select2',
                            'width': '220'
                        }
                    )
                )
            },
        ))

        parameters['G2'] = self.get_wrapped_parameters((
            {
                'name': 'indicator',
                'field': forms.ChoiceField(
                    label='Select Indicator',
                    choices=indicator_choices,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    )
                )
            },
        ))
        return parameters

    def get_context_data(self, **kwargs):
        context = super(WardPrioritizationMapReportView, self).get_context_data(**kwargs)
        context['title'] = "Ward prioritization index"
        context['SEF'] = self.prepare_ward_wise_total_sef_grantees()
        context['SEF_grantees_data'] = self.prepare_sef_grantees()
        context['SIF'] = self.prepare_ward_wise_total_sif_intervention()
        context['SIF_intervention_data'] = self.prepare_sif_intervention()
        return context

    def prepare_ward_wise_total_sef_grantees(self):
        ward_queryset = Geography.objects.filter(
            level__name='Ward'
        ).values('id', 'name', 'parent')
        ward_id_dict = dict()
        for ward in ward_queryset:
            ward_id_dict[str(ward['name']) + '_' + str(ward['parent'])] = ward['id']

        queryset = SEFGranteesInfoCache.objects.filter(city__isnull=False).exclude(ward=None).values('city_id', 'ward') \
            .annotate(
            Sum('no_of_business_grantee'),
            Sum('no_of_apprenticeship_grantee'),
            Sum('no_of_education_dropout_grantee'),
            Sum('no_education_early_marriage_grantee')
        )

        ward_dict = dict()
        geography_ids = list(Geography.objects.filter(
            level__name='Ward'
        ).values_list('pk', flat=True))
        for geography_id in geography_ids:
            ward_dict[geography_id] = {
                'SEF': 0
            }
        for q in queryset:
            ward_id = ward_id_dict.get(str(q['ward']) + '_' + str(q['city_id']))
            if ward_id:
                ward_dict[ward_id]['SEF'] = q['no_of_business_grantee__sum']
                ward_dict[ward_id]['SEF'] += q['no_of_apprenticeship_grantee__sum']
                ward_dict[ward_id]['SEF'] += q['no_of_education_dropout_grantee__sum']
                ward_dict[ward_id]['SEF'] += q['no_education_early_marriage_grantee__sum']

        return ward_dict

    def prepare_sef_grantees(self):
        geography_ids = list(Geography.objects.filter(
            level__name='Ward'
        ).values_list('pk', flat=True))
        result = dict()
        for geography_id in geography_ids:
            result[geography_id] = {
                'Number of Business Grantees': 0,
                'Number of Apprenticeship Grantees': 0,
                'Number of School Drop-Out Prevention Grantees': 0,
                'Number of Early Marriage Prevention Grantees': 0,
            }

        geography_queryset = Geography.objects.filter(id__in=geography_ids, type='Ward').values('name', 'id', 'parent')
        geography_id_dict = {str(item['name']) + '_' + str(item['parent']): item['id'] for item in geography_queryset}

        _queryset = SEFGranteesInfoCache.objects.filter(city__isnull=False).exclude(ward=None).values('city_id',
                                                                                                      'ward'). \
            annotate(Sum(F('no_of_business_grantee')), Sum(F('no_of_apprenticeship_grantee')),
                     Sum(F('no_of_education_dropout_grantee')), Sum(F('no_education_early_marriage_grantee')))

        for _item in _queryset:
            if _item['city_id'] and _item['ward']:
                ward_no = geography_id_dict.get(str(_item['ward']) + '_' + str(_item['city_id'])) \
                          or geography_id_dict.get((str(_item['ward']).zfill(2)) + '_' + str(_item['city_id']))
                if ward_no:
                    result[ward_no]['Number of Business Grantees'] = _item['no_of_business_grantee__sum'] or 0
                    result[ward_no]['Number of Apprenticeship Grantees'] = _item[
                                                                               'no_of_apprenticeship_grantee__sum'] or 0
                    result[ward_no]['Number of School Drop-Out Prevention Grantees'] = _item[
                                                                                  'no_of_education_dropout_grantee__sum'] or 0
                    result[ward_no]['Number of Early Marriage Prevention Grantees'] = _item[
                                                                                             'no_education_early_marriage_grantee__sum'] or 0

        return result

    def prepare_ward_wise_total_sif_intervention(self):
        all_intervention_type = [
            'Single pit latrine', 'Twin pit latrine', 'Community Latrine', 'Deep Tubewell',
            'Shallow Tubewell', 'Deepset Tubewell', 'Deep tubewell with submersible pump',
            'Drain and/or Culvert', 'Footpath'
        ]
        queryset = Intervention.objects.filter(
            type_of_intervention__in=all_intervention_type,
            sif__assigned_cdc__address__geography__isnull=False
        ).distinct().values(
            'sif__assigned_cdc__address__geography_id'
        ).annotate(Sum('number_of_facilities'))

        ward_dict = dict()
        for q in queryset:
            if q['sif__assigned_cdc__address__geography_id'] not in ward_dict:
                ward_dict[q['sif__assigned_cdc__address__geography_id']] = dict()
            ward_dict[q['sif__assigned_cdc__address__geography_id']]['SIF'] = q['number_of_facilities__sum'] or 0

        return ward_dict

    def prepare_sif_intervention(self):
        latrine = [
            'Single pit latrine',
            'Twin pit latrine',
            'Community Latrine'
        ]
        tubewell = [
            'Deep Tubewell',
            'Shallow Tubewell',
            'Deepset Tubewell',
            'Deep tubewell with submersible pump'
        ]
        drain = [
            'Drain and/or Culvert',
        ]
        footpath = [
            'Footpath',
        ]
        intervention_type_dict = {
            'Number of Latrine': latrine,
            'Number of Tubewell': tubewell,
            'Number of Drain': drain,
            'Number of Footpath': footpath
        }
        geography_ids = list(Geography.objects.filter(
            level__name='Ward'
        ).values_list('pk', flat=True))

        result = dict()
        for geography_id in geography_ids:
            result[geography_id] = {
                'Number of Latrine': 0,
                'Number of Tubewell': 0,
                'Number of Drain': 0,
                'Number of Footpath': 0
            }

        all_intervention_type = [
            'Single pit latrine', 'Twin pit latrine', 'Community Latrine', 'Deep Tubewell',
            'Shallow Tubewell', 'Deepset Tubewell', 'Deep tubewell with submersible pump',
            'Drain and/or Culvert', 'Footpath'
        ]

        queryset = Intervention.objects.filter(
            type_of_intervention__in=all_intervention_type,
            sif__assigned_cdc__address__geography__isnull=False
        ).distinct()

        for _key, _types in intervention_type_dict.items():
            _queryset = queryset.filter(
                type_of_intervention__in=_types
            ).values(
                'sif__assigned_cdc__address__geography_id'
            ).annotate(Sum(F('number_of_facilities')))

            for _item in _queryset:
                total_facilities = _item['number_of_facilities__sum'] or 0
                result[_item['sif__assigned_cdc__address__geography_id']][_key] = total_facilities

        return result

    def get_json_response(self, content, **kwargs):
        city_id = self.extract_parameter('city')
        indicator = self.extract_parameter('indicator')

        if not city_id:
            cities = Geography.objects.filter(level__name='Pourashava/City Corporation').values('id',)
            _ids = [_city['id'] for _city in cities]
            _ids.append(indicator)
        else:
            _ids = [city_id, indicator]

        data_dict = dict()
        data_dict['title'] = "Ward prioritization index"
        data_dict['data'] = _ids

        return super(WardPrioritizationMapReportView, self).get_json_response(
            self.convert_context_to_json(data_dict), **kwargs)
