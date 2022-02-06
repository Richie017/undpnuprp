from collections import OrderedDict

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
from undp_nuprp.approvals.models import LowCostHousingUnit
from undp_nuprp.reports.models.interactive_maps.output_four.low_cost_housing_unit_map_report import \
    LowCostHousingUnitMapReport
from undp_nuprp.reports.views.interactive_maps.interactive_map_report import GenericInteractiveMapReportView

__author__ = 'Kaikobud'


@decorate(override_view(model=LowCostHousingUnitMapReport, view=ViewActionEnum.Manage))
class LowCostHousingUnitMapReportView(GenericInteractiveMapReportView):
    def get_template_names(self):
        return ['reports/interactive-map-city-ward.html']

    def get_report_parameters(self, **kwargs):
        request = CrequestMiddleware.get_request()
        parameters = super(LowCostHousingUnitMapReportView, self).get_report_parameters(**kwargs)
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
        context = super(LowCostHousingUnitMapReportView, self).get_context_data(**kwargs)
        context['title'] = "Number of Low-Cost Housing Units"

        city_ids = list(Geography.objects.filter(
            level__name='Pourashava/City Corporation'
        ).values_list('id', flat=True))

        context['color_range'] = self.prepare_color_range(city_ids)
        context['total_strategy'] = self.prepare_city_wise_total_data(city_ids)
        context['legend_label'] = "Number of Housing Units"
        return context

    @classmethod
    def prepare_color_range(cls, city_ids):
        queryset = LowCostHousingUnit.objects.values('ward__parent_id').annotate(Sum('number_of_housing_units'))

        color_dict = dict()
        color_dict['city_range'] = ['> 0', ]
        color_dict['ward_range'] = ['> 0', ]
        for city in city_ids:
            color_dict[city] = 0  # default color range

        if queryset.exists():
            _key = 'number_of_housing_units__sum'
            range_min = queryset.order_by(_key)[0][_key] or 0
            range_max = queryset.order_by('-' + _key)[0][_key] or 0
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
                    color_dict["city_range"] += [str(int(range_min) + (i - 1))+".01" + ' - ' + str(int(range_min) + i), ]
                for q in queryset:
                    city_id = q['ward__parent_id']
                    count = q[_key] or 0
                    
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
                    '> '+str(range3),
                ]

                for q in queryset:
                    city_id = q['ward__parent_id']
                    count = q[_key] or 0
                    
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

        queryset_for_ward = LowCostHousingUnit.objects.values('ward_id').annotate(Sum('number_of_housing_units'))

        if queryset_for_ward.exists():
            _key = 'number_of_housing_units__sum'
            range_min = queryset_for_ward.order_by(_key)[0][_key] or 0
            range_max = queryset_for_ward.order_by('-' + _key)[0][_key] or 0
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
                    color_dict["ward_range"] += [str(int(range_min) + (i - 1))+".01" + ' - ' + str(int(range_min) + i), ]
                for q in queryset_for_ward:
                    ward_id = q['ward_id']
                    count = q[_key] or 0
                    
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
                    '> '+str(range3),
                ]

                for q in queryset_for_ward:
                    ward_id = q['ward_id']
                    count = q[_key] or 0
                    
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
        queryset = LowCostHousingUnit.objects.values('ward__parent_id').annotate(Sum('number_of_housing_units'))

        total_key = 'Units'
        result = dict()
        for city in city_ids:
            result[city] = {
                total_key: 0
            }

        for _item in queryset:
            result[_item['ward__parent_id']][total_key] = _item['number_of_housing_units__sum'] or 0

        return result

    @classmethod
    def prepare_low_cost_housing_units_data(cls, ward_ids=None, city_ids=None):

        # prepare data
        queryset = LowCostHousingUnit.objects.filter(
            ward__isnull=False
        )
        if ward_ids:
            queryset = queryset.filter(ward_id__in=ward_ids)
            geography_ids = ward_ids + city_ids
        elif city_ids:
            queryset = queryset.filter(ward__parent_id__in=city_ids)
            geography_ids = city_ids + list(Geography.objects.filter(
                level__name='Ward', parent__in=city_ids
            ).values_list('pk', flat=True))
        else:
            geography_ids = list(Geography.objects.filter(
                level__name__in=['Pourashava/City Corporation', 'Ward']
            ).values_list('pk', flat=True))

        result = dict()
        for geography_id in geography_ids:
            result[geography_id] = OrderedDict()
            result[geography_id]['No. of Housing Units'] = 0
            result[geography_id]['Number of PG Members benefiting (Male)'] = 0
            result[geography_id]['Number of PG Members benefiting (Female)'] = 0
            result[geography_id]['Number of Non-PG Members benefiting (Male)'] = 0
            result[geography_id]['Number of Non-PG Members benefiting (Female)'] = 0
            result[geography_id]['Number of people with disabilities (Male)'] = 0
            result[geography_id]['Number of people with disabilities (Female)'] = 0

        _queryset = queryset.values(
            'ward_id',
            'ward__parent_id'
        ).annotate(Sum(F('number_of_housing_units')),
                   Sum(F('number_of_male_pg_member_benefiting')), Sum(F('number_of_female_pg_member_benefiting')),
                   Sum(F('number_of_male_non_pg_member_benefiting')),
                   Sum(F('number_of_female_non_pg_member_benefiting')),
                   Sum(F('number_of_male_with_disabilities')), Sum(F('number_of_female_with_disabilities')))

        for _item in _queryset:
            result[_item['ward_id']]['No. of Housing Units'] = _item['number_of_housing_units__sum'] or 0
            result[_item['ward__parent_id']]['No. of Housing Units'] += _item['number_of_housing_units__sum'] or 0
            result[_item['ward_id']]['Number of PG Members benefiting (Male)'] = \
                _item['number_of_male_pg_member_benefiting__sum'] or 0
            result[_item['ward__parent_id']]['Number of PG Members benefiting (Male)'] += \
                _item['number_of_male_pg_member_benefiting__sum'] or 0
            result[_item['ward_id']]['Number of PG Members benefiting (Female)'] = \
                _item['number_of_female_pg_member_benefiting__sum'] or 0
            result[_item['ward__parent_id']]['Number of PG Members benefiting (Female)'] += \
                _item['number_of_female_pg_member_benefiting__sum'] or 0
            result[_item['ward_id']]['Number of Non-PG Members benefiting (Male)'] = \
                _item['number_of_male_non_pg_member_benefiting__sum'] or 0
            result[_item['ward__parent_id']]['Number of Non-PG Members benefiting (Male)'] += \
                _item['number_of_male_non_pg_member_benefiting__sum'] or 0
            result[_item['ward_id']]['Number of Non-PG Members benefiting (Female)'] = \
                _item['number_of_female_non_pg_member_benefiting__sum'] or 0
            result[_item['ward__parent_id']]['Number of Non-PG Members benefiting (Female)'] += \
                _item['number_of_female_non_pg_member_benefiting__sum'] or 0
            result[_item['ward_id']]['Number of people with disabilities (Male)'] = \
                _item['number_of_male_with_disabilities__sum'] or 0
            result[_item['ward__parent_id']]['Number of people with disabilities (Male)'] += \
                _item['number_of_male_with_disabilities__sum'] or 0
            result[_item['ward_id']]['Number of people with disabilities (Female)'] = \
                _item['number_of_female_with_disabilities__sum'] or 0
            result[_item['ward__parent_id']]['Number of people with disabilities (Female)'] += \
                _item['number_of_female_with_disabilities__sum'] or 0

        return result

    def get_json_response(self, content, **kwargs):
        city_ids = self.str_to_list(self.extract_parameter('city'))
        ward_ids = self.str_to_list(self.extract_parameter('ward'))

        data_dict = dict()
        data_dict['title'] = "Number of Low-Cost Housing Units Location Map"
        data_dict['data'] = self.prepare_low_cost_housing_units_data(ward_ids, city_ids)

        return super(LowCostHousingUnitMapReportView, self).get_json_response(
            self.convert_context_to_json(data_dict), **kwargs)
