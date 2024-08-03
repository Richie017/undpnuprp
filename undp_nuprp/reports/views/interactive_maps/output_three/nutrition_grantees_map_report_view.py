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
from config.model_json_cache import MODEL_JASON_URL
from settings import INSTALLED_APPS
from undp_nuprp.reports.models import SEFGranteesInfoCache, NutritionGranteesMapReport
from undp_nuprp.reports.views.interactive_maps.interactive_map_report import GenericInteractiveMapReportView

__author__ = 'Kaikobud'


@decorate(override_view(model=NutritionGranteesMapReport, view=ViewActionEnum.Manage))
class NutritionGranteesMapReportView(GenericInteractiveMapReportView):
    def get_template_names(self):
        return ['reports/interactive-map-city-ward.html']

    def get_report_parameters(self, **kwargs):
        request = CrequestMiddleware.get_request()
        parameters = super(NutritionGranteesMapReportView, self).get_report_parameters(**kwargs)
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
        context = super(NutritionGranteesMapReportView, self).get_context_data(**kwargs)
        context['title'] = "Number of Nutrition Grantees"

        city_ids = list(Geography.objects.filter(
            level__name='Pourashava/City Corporation'
        ).values_list('id', flat=True))

        context['color_range'] = self.prepare_color_range(city_ids)
        context['total_strategy'] = self.prepare_city_wise_total_data(city_ids)
        context['legend_label'] = "Number of Grantees"
        return context

    @classmethod
    def prepare_color_range(cls, city_ids):
        queryset = SEFGranteesInfoCache.objects.filter(
            city__isnull=False
        ).values('city_id').annotate(Sum(F('no_of_nutrition_grantees')))

        color_dict = dict()
        color_dict['city_range'] = ['> 0', ]
        color_dict['ward_range'] = ['> 0', ]
        for city in city_ids:
            color_dict[city] = 0  # default color range

        if queryset.exists():
            _key = 'no_of_nutrition_grantees__sum'
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
                    color_dict["city_range"] += [
                        str(int(range_min) + (i - 1))+".01" + ' - ' + str(int(range_min) + i), ]
                for q in queryset:
                    city_id = q['city_id']
                    count = q[_key]

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
                    city_id = q['city_id']
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

        ward_queryset = Geography.objects.filter(
            level__name='Ward', parent_id__in=city_ids
        ).values('id', 'name', 'parent')
        ward_id_dict = dict()
        for ward in ward_queryset:
            color_dict[ward['id']] = 0  # default color range
            ward_id_dict[str(ward['name']) + '_' + str(ward['parent'])] = ward['id']


        queryset = SEFGranteesInfoCache.objects.filter(
            city__isnull=False
        ).exclude(ward__isnull=True).exclude(ward="").values('city_id', 'ward').annotate(
            Sum('no_of_nutrition_grantees'),
        )

        ward_dict = dict()
        for q in queryset:
            ward_dict[str(q['city_id']) + '_' + str(q['ward'])] = q['no_of_nutrition_grantees__sum']

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
                for q, v in ward_dict:
                    ward_id = ward_id_dict.get(str(q['ward']) + '_' + str(q['city_id']))
                    count = 0
                    if ward_id:
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
                    city_id, ward = q.split('_')
                    ward_id = ward_id_dict.get(str(ward) + '_' + str(city_id))
                    if ward_id:
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
        _queryset = SEFGranteesInfoCache.objects.filter(city__isnull=False).\
            values('city_id').annotate(Sum(F('no_of_nutrition_grantees')))

        total_key = 'Grantees'
        result = dict()
        for city in city_ids:
            result[city] = {
                total_key: 0
            }

        for _item in _queryset:
            result[_item['city_id']][total_key] = _item['no_of_nutrition_grantees__sum'] or 0

        return result

    @classmethod
    def prepare_number_of_nutrition_grantees_data(cls, city_ids=None, ward_ids=None):
        queryset = SEFGranteesInfoCache.objects.filter(city__isnull=False)

        if ward_ids:
            ward_names = list(Geography.objects.filter(
                level__name='Ward', parent__in=city_ids
            ).values_list('name', flat=True))
            ward_names = [name.zfill(2) for name in ward_names]
            queryset = queryset.filter(city__in=city_ids, ward__in=ward_names)
            geography_ids = ward_ids + city_ids
        elif city_ids:
            queryset = queryset.filter(city__in=city_ids)
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
                'Number of Nutrition Grantees': 0
            }

        geography_queryset = Geography.objects.filter(id__in=geography_ids, type='Ward').values('name', 'id', 'parent')
        geography_id_dict = {str(item['name']) + '_' + str(item['parent']): item['id'] for item in geography_queryset}

        _queryset = queryset.values('city_id', 'ward'). \
            annotate(Sum(F('no_of_nutrition_grantees')))

        for _item in _queryset:
            if _item['city_id'] and _item['ward']:
                ward_no = geography_id_dict.get(str(_item['ward']) + '_' + str(_item['city_id'])) \
                          or geography_id_dict.get((str(_item['ward']).zfill(2)) + '_' + str(_item['city_id']))
                if ward_no:
                    result[ward_no]['Number of Nutrition Grantees'] = _item['no_of_nutrition_grantees__sum'] or 0
                    result[_item['city_id']]['Number of Nutrition Grantees'] += _item['no_of_nutrition_grantees__sum'] or 0
        return result

    def get_json_response(self, content, **kwargs):
        city_ids = self.str_to_list(self.extract_parameter('city'))
        ward_ids = self.str_to_list(self.extract_parameter('ward'))

        data_dict = dict()
        data_dict['title'] = "Number of Nutrition Grantees"
        data_dict['data'] = self.prepare_number_of_nutrition_grantees_data(city_ids, ward_ids)

        return super(NutritionGranteesMapReportView, self).get_json_response(
            self.convert_context_to_json(data_dict), **kwargs)
