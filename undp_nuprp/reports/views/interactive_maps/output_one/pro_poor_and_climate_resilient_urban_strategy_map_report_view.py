from django import forms
from django.db.models import F, Count, Q

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.models.geography.geography import Geography
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.models import CitiesTownsWithProPoorClimateResilientUrbanStrategy
from undp_nuprp.reports.models import ProPoorClimateResilientUrbanStrategyMapReport
from undp_nuprp.reports.views.interactive_maps.interactive_map_report import GenericInteractiveMapReportView

__author__ = 'Kaikobud'

Status_Choices = \
    (('', 'Select One'), ('Yes', 'Yes'), ('No', 'No'), ('Ongoing', 'Ongoing'), ('Not applicable', 'Not applicable'))
Stage_choices = \
    (('', 'Select One'), ('Stage 1', 'Stage 1'), ('Stage 2', 'Stage 2'), ('Stage 3', 'Stage 3'))
Name_of_Assessment_Choices = \
    (('', 'Select one'),
     ("Poverty Mapping / Assessment", "Poverty Mapping / Assessment"),
     ("Mapping donor efforts in the city", "Mapping donor efforts in the city"),
     ("Standing Committee and Coordination Committee Assessment of the Local Government",
      "Standing Committee and Coordination Committee Assessment of the Local Government"),
     ("Institutional and Financial Capacity Assessment of the Local Government",
      "Institutional and Financial Capacity Assessment of the Local Government"),
     ("CDC Capacity Assessment", "CDC Capacity Assessment"),
     ("Capacity Assessment of CDC Town Federation", "Capacity Assessment of CDC Town Federation"),
     ("PG Member Registration", "PG Member Registration"),
     ("Local job market assessment", "Local job market assessment"),
     ("Gender Based Violence Assessment", "Gender Based Violence Assessment"),
     ("Nutrition Assessment", "Nutrition Assessment",),
     ("Disability Assessment", "Disability Assessment"),
     ("Infrastructure Assessment", "Infrastructure Assessment"),
     ("Climate Change Vulnerability Assessment (CCVA)", "Climate Change Vulnerability Assessment (CCVA)"),
     ("Vacant Land Mapping/Assessment (VLM)", "Vacant Land Mapping/Assessment (VLM)"),
     ("Housing and Land Tenure Assessment", "Housing and Land Tenure Assessment")
     )
Name_of_Component_Choices = \
    (('', 'Select one'),
     ('Improved coordination, planning and management in programme towns and cities',
      'Improved coordination, planning and management in programme towns and cities'),
     ('Enhanced organization, capability and effective voice of poor urban communities',
      'Enhanced organization, capability and effective voice of poor urban communities'),
     ('Improved well-being in poor urban slums particularly for women and girls',
      ' Improved well-being in poor urban slums particularly for women and girls'),
     ('More secure land tenure and housing in programme towns and cities',
      'More secure land tenure and housing in programme towns and cities'),
     ('More and better climate-resilient and community-based infrastructure in programme towns and cities',
      'More and better climate-resilient and community-based infrastructure in programme towns and cities'),
     )


@decorate(override_view(model=ProPoorClimateResilientUrbanStrategyMapReport, view=ViewActionEnum.Manage))
class ProPoorClimateResilientUrbanStrategyMapReportView(GenericInteractiveMapReportView):
    def get_template_names(self):
        return ['reports/interactive-map-pro-poor-climate-resilient.html']

    def get_report_parameters(self, **kwargs):
        parameters = super(ProPoorClimateResilientUrbanStrategyMapReportView, self).get_report_parameters(**kwargs)
        parameters['G1'] = self.get_wrapped_parameters((
            {
                'name': 'stage',
                'field': forms.ChoiceField(
                    label='Select Stage',
                    choices=Stage_choices,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    )
                )
            },
            {
                'name': 'name_of_assessment',
                'field': forms.ChoiceField(
                    label='Select Assessment',
                    choices=Name_of_Assessment_Choices,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    )
                )
            }
        ))
        parameters['G2'] = self.get_wrapped_parameters((
            {
                'name': 'city',
                'field': GenericModelChoiceField(
                    queryset=Geography.objects.filter(level__name='Pourashava/City Corporation').order_by('name'),
                    label='Select City',
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
            {
                'name': 'status',
                'field': forms.ChoiceField(
                    label='Select Status',
                    choices=Status_Choices,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    )
                )
            }
        ))
        parameters['G3'] = self.get_wrapped_parameters((
            {
                'name': 'name_of_component',
                'field': forms.ChoiceField(
                    label='Select Component',
                    choices=Name_of_Component_Choices,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    )
                )
            },
        ))
        return parameters

    def get_context_data(self, **kwargs):
        context = super(ProPoorClimateResilientUrbanStrategyMapReportView, self).get_context_data(**kwargs)
        context['title'] = "Pro Poor & Climate Resilient Urban Strategy Under Implementation"
        context['has_second_layer'] = 0  # 1 - True, 0 - False
        context['color_range'] = self.prepare_color_range()
        return context

    @classmethod
    def prepare_color_range(cls):
        cities = Geography.objects.filter(level__name='Pourashava/City Corporation').values('id')
        city_ids = [_city['id'] for _city in cities]

        queryset = CitiesTownsWithProPoorClimateResilientUrbanStrategy.objects.values(
            'city_id'
        ).annotate(Count(F('id')))

        color_dict = dict()
        color_dict['city_range'] = ['> 0', ]
        for city in city_ids:
            color_dict[city] = 0  # default color range

        if queryset.exists():
            range_min = queryset.order_by('id__count')[0]['id__count']
            range_max = queryset.order_by('-id__count')[0]['id__count']
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
                for i in range(1, range_diff + 1):
                    color_dict["city_range"] += [str(range_min + (i - 1))+".01" + ' - ' + str(range_min + i), ]
                for q in queryset:
                    city_id = q['city_id']
                    count = q['id__count'] or 0

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

                for q in queryset:
                    city_id = q['city_id']
                    count = q['id__count'] or 0
                    
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
        return color_dict

    @classmethod
    def prepare_data(cls, queries):

        # prepare data
        queryset = CitiesTownsWithProPoorClimateResilientUrbanStrategy.objects.all()
        cities = Geography.objects.filter(level__name='Pourashava/City Corporation').values('id')
        city_ids = [_city['id'] for _city in cities]
        if queries:
            queryset = queryset.filter(queries)
            city_ids = set([item['city_id'] for item in queryset.values('city_id')])
        result = dict()
        _queryset = queryset.values(
            'city_id'
        ).annotate(Count(F('id')))
        for city in city_ids:
            result[city] = dict()
            result[city]['No. of Pro Poor & Climate Resilient Urban Strategy Under Implementation'] = 0

        for _item in _queryset:
            result[_item['city_id']]['No. of Pro Poor & Climate Resilient Urban Strategy Under Implementation'] = \
                _item['id__count'] or 0

        return result

    @classmethod
    def prepare_city_wise_total_data(cls):

        # prepare data
        queryset = CitiesTownsWithProPoorClimateResilientUrbanStrategy.objects.all()
        cities = Geography.objects.filter(level__name='Pourashava/City Corporation').values('id')
        city_ids = [_city['id'] for _city in cities]
        result = dict()
        _queryset = queryset.values(
            'city_id'
        ).annotate(Count(F('id')))
        for city in city_ids:
            result[city] = dict()
            result[city]['total_strategies'] = 0

        for _item in _queryset:
            result[_item['city_id']]['total_strategies'] = \
                _item['id__count'] or 0

        return result

    @classmethod
    def prepare_fields_lookups(cls, parameters):
        and_query = None
        for field_name, field_value in parameters.items():
            if field_value:
                if field_name == 'city':
                    q = Q(**{str(field_name) + '_id': int(field_value)})
                else:
                    q = Q(**{str(field_name) + '__iexact': field_value})
                if and_query is None:
                    and_query = q
                else:
                    and_query &= q
        return and_query

    def get_json_response(self, content, **kwargs):
        stage = self.extract_parameter('stage')
        city = self.extract_parameter('city')
        name_of_component = self.extract_parameter('name_of_component')
        name_of_assessment = self.extract_parameter('name_of_assessment')
        status = self.extract_parameter('status')
        parameters_dict = {
            'stage': stage,
            'city': city,
            'name_of_component': name_of_component,
            'name_of_assessment': name_of_assessment,
            'status': status
        }
        _queries = self.prepare_fields_lookups(parameters_dict)

        data_dict = dict()
        data_dict['title'] = "Pro Poor & Climate Resilient Urban Strategy Under Implementation Location Map"
        data_dict['total_strategy'] = self.prepare_city_wise_total_data()
        data_dict['data'] = self.prepare_data(_queries)

        return super(ProPoorClimateResilientUrbanStrategyMapReportView, self).get_json_response(
            self.convert_context_to_json(data_dict), **kwargs)
