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
from undp_nuprp.nuprp_admin.models import CommunityActionPlan
from undp_nuprp.reports.models.interactive_maps.output_two.community_action_plan_map_report import \
    CommunityActionPlanMapReport
from undp_nuprp.reports.views.interactive_maps.interactive_map_report import GenericInteractiveMapReportView

__author__ = 'Kaikobud'


@decorate(override_view(model=CommunityActionPlanMapReport, view=ViewActionEnum.Manage))
class CommunityActionPlanMapReportView(GenericInteractiveMapReportView):
    def get_template_names(self):
        return ['reports/interactive-map-city-ward.html']

    def get_report_parameters(self, **kwargs):
        request = CrequestMiddleware.get_request()
        parameters = super(CommunityActionPlanMapReportView, self).get_report_parameters(**kwargs)
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
        context = super(CommunityActionPlanMapReportView, self).get_context_data(**kwargs)
        context['title'] = "Number of Community Action Plan"

        city_ids = list(Geography.objects.filter(
            level__name='Pourashava/City Corporation'
        ).values_list('id', flat=True))

        context['color_range'] = self.prepare_color_range(city_ids)
        context['total_strategy'] = self.prepare_city_wise_total_data(city_ids)
        context['legend_label'] = "Number of CAPs"
        return context

    @classmethod
    def prepare_color_range(cls, city_ids):
        queryset = CommunityActionPlan.objects.exclude(ward_no='').values('city_id').annotate(Sum('cap_developed'))

        color_dict = dict()
        color_dict['city_range'] = ['> 0', ]
        color_dict['ward_range'] = ['> 0', ]
        for city in city_ids:
            color_dict[city] = 0  # default color range

        if queryset.exists():
            _key = 'cap_developed__sum'
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
                for i in range(1, range_diff + 1):
                    color_dict["city_range"] += [str(range_min + (i - 1))+".01" + ' - ' + str(range_min + i), ]
                for q in queryset:
                    city_id = q['city_id']
                    count = q[_key] or 0

                    if count == 0:
                        continue
                    elif count <= range1:
                        color_dict[city_id] = 1
                    elif range1 < count <= range_min + 1:
                        color_dict[city_id] = 2
                    elif range1 + 1 < count <= range_min + 2:
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

        queryset_for_ward = CommunityActionPlan.objects.exclude(
            ward_no=''
        ).values('city_id', 'ward_no').annotate(Sum('cap_developed'))

        if queryset_for_ward.exists():
            _key = 'cap_developed__sum'
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
                    ward_id = ward_id_dict.get(str(q['ward_no']) + '_' + str(q['city_id']))
                    if ward_id:
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
                    '> ' + str(range3),
                ]

                for q in queryset_for_ward:
                    ward_id = ward_id_dict.get(str(q['ward_no']) + '_' + str(q['city_id']))
                    if ward_id:
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
        queryset = CommunityActionPlan.objects.exclude(ward_no='').values('city_id').annotate(Sum('cap_developed'))

        total_key = 'CAPs'
        result = dict()
        for city in city_ids:
            result[city] = {
                total_key: 0
            }

        for _item in queryset:
            result[_item['city_id']][total_key] = _item['cap_developed__sum'] or 0

        return result

    @classmethod
    def prepare_community_action_pan_data(cls, ward_ids=None, city_ids=None):

        # prepare data
        queryset = CommunityActionPlan.objects.filter(
            city__isnull=False,
            cap_developed__isnull=False). \
            exclude(ward_no='')
        if ward_ids:
            ward_name_list = list(Geography.objects.filter(id__in=ward_ids).values_list('name', flat=True))
            queryset = queryset.filter(ward_no__in=ward_name_list)
            geography_ids = ward_ids + city_ids
        elif city_ids:
            queryset = queryset.filter(city_id__in=city_ids)
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
                'Number of CAP developed': 0
            }

        geography_queryset = Geography.objects.filter(id__in=geography_ids, type='Ward').values('name', 'id', 'parent')
        geography_id_dict = {str(item['name']) + '_' + str(item['parent']): item['id'] for item in geography_queryset}

        _queryset = queryset.values(
            'city_id',
            'ward_no'
        ).annotate(Sum(F('cap_developed')))

        for _item in _queryset:
            total_cap_developed = _item['cap_developed__sum'] or 0
            word_no = geography_id_dict.get(str(_item['ward_no']) + '_' + str(_item['city_id'])) \
                      or geography_id_dict.get((str(_item['ward_no']).zfill(2)) + '_' + str(_item['city_id']))
            if word_no:
                result[word_no]['Number of CAP developed'] = total_cap_developed
                result[_item['city_id']]['Number of CAP developed'] += total_cap_developed

        return result

    def get_json_response(self, content, **kwargs):
        city_ids = self.str_to_list(self.extract_parameter('city'))
        ward_ids = self.str_to_list(self.extract_parameter('ward'))

        data_dict = dict()
        data_dict['title'] = "Number of Community Action Plan Location Map"
        data_dict['data'] = self.prepare_community_action_pan_data(ward_ids, city_ids)

        return super(CommunityActionPlanMapReportView, self).get_json_response(
            self.convert_context_to_json(data_dict), **kwargs)
