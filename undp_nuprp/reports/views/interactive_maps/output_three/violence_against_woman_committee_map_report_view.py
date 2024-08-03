from django import forms
from django.db.models import Sum, F

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.models import GeographyLevel
from blackwidow.core.models.geography.geography import Geography
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.approvals.models import ViolenceAgainstWomanCommittee
from undp_nuprp.reports.models import ViolenceAgainstWomanCommitteeMapReport
from undp_nuprp.reports.views.interactive_maps.interactive_map_report import GenericInteractiveMapReportView

__author__ = 'Kaikobud'


@decorate(override_view(model=ViolenceAgainstWomanCommitteeMapReport, view=ViewActionEnum.Manage))
class ViolenceAgainstWomanCommitteeMapReportView(GenericInteractiveMapReportView):
    def get_template_names(self):
        return ['reports/interactive-map-city.html']

    def get_report_parameters(self, **kwargs):
        parameters = super(ViolenceAgainstWomanCommitteeMapReportView, self).get_report_parameters(**kwargs)

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
        return parameters

    def get_context_data(self, **kwargs):
        context = super(ViolenceAgainstWomanCommitteeMapReportView, self).get_context_data(**kwargs)
        context['title'] = "Number of Violence Against Woman Committees"
        context['has_second_layer'] = 0  # 1 - True, 0 - False
        city_ids = list(Geography.objects.filter(
            level__name='Pourashava/City Corporation'
        ).values_list('id', flat=True))

        context['color_range'] = self.prepare_color_range(city_ids)
        context['total_strategy'] = self.prepare_city_wise_total_data(city_ids)
        context['legend_label'] = "Number of Committees"
        return context

    @classmethod
    def prepare_color_range(cls, city_ids):
        queryset = ViolenceAgainstWomanCommittee.objects.values(
            'city_id'
        ).annotate(Sum('number_of_violence_against_woman_committees'))

        color_dict = dict()
        color_dict['city_range'] = ['> 0', ]
        for city in city_ids:
            color_dict[city] = 0  # default color range

        if queryset.exists():
            _key = 'number_of_violence_against_woman_committees__sum'
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
        return color_dict

    @classmethod
    def prepare_city_wise_total_data(cls, city_ids):
        _queryset = ViolenceAgainstWomanCommittee.objects.values(
            'city_id'
        ).annotate(Sum('number_of_violence_against_woman_committees'))

        total_key = 'Committees'
        result = dict()
        for city in city_ids:
            result[city] = {
                total_key: 0
            }

        for _item in _queryset:
            result[_item['city_id']][total_key] = _item['number_of_violence_against_woman_committees__sum'] or 0

        return result

    @classmethod
    def prepare_number_of_violence_against_woman_committees_data(cls, city_ids=None):

        queryset = ViolenceAgainstWomanCommittee.objects.filter(city__isnull=False)
        if city_ids:
            queryset = queryset.filter(city__in=city_ids)
            geography_ids = city_ids
        else:
            geography_ids = list(Geography.objects.filter(
                level__name='Pourashava/City Corporation'
            ).values_list('pk', flat=True))

        result = dict()
        for geography_id in geography_ids:
            result[geography_id] = {
                'Number of Violence Against Woman Committees': 0
            }

        _queryset = queryset.values('city_id').annotate(Sum(F('number_of_violence_against_woman_committees')))

        for _item in _queryset:
            if _item['city_id']:
                result[_item['city_id']]['Number of Violence Against Woman Committees'] = \
                    _item['number_of_violence_against_woman_committees__sum'] or 0
        return result

    def get_json_response(self, content, **kwargs):
        city_ids = self.str_to_list(self.extract_parameter('city'))

        data_dict = dict()
        data_dict['title'] = "Number of Violence Against Woman Committees"
        data_dict['data'] = self.prepare_number_of_violence_against_woman_committees_data(city_ids)

        return super(ViolenceAgainstWomanCommitteeMapReportView, self).get_json_response(
            self.convert_context_to_json(data_dict), **kwargs)
