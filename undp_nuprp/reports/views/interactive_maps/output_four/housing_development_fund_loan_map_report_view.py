from django import forms
from django.db.models import F, Count

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.models import GeographyLevel
from blackwidow.core.models.geography.geography import Geography
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models import CommunityHousingDevelopmentFund
from undp_nuprp.reports.models.interactive_maps.output_four.housing_development_fund_loan_map_report import \
    CHDFLoanMapReport
from undp_nuprp.reports.views.interactive_maps.interactive_map_report import GenericInteractiveMapReportView

__author__ = 'Ziaul Haque'


@decorate(override_view(model=CHDFLoanMapReport, view=ViewActionEnum.Manage))
class CHDFLoanMapReportView(GenericInteractiveMapReportView):
    def get_template_names(self):
        return ['reports/interactive-map-city.html']

    def get_report_parameters(self, **kwargs):
        parameters = super(CHDFLoanMapReportView, self).get_report_parameters(**kwargs)

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
        context = super(CHDFLoanMapReportView, self).get_context_data(**kwargs)
        context['title'] = "Number of Households Received Housing Loan from CHDF"
        context['has_second_layer'] = 0  # 1 - True, 0 - False

        city_ids = list(Geography.objects.filter(
            level__name='Pourashava/City Corporation'
        ).values_list('id', flat=True))

        context['color_range'] = self.prepare_color_range(city_ids)
        context['total_strategy'] = self.prepare_city_wise_total_data(city_ids)
        context['legend_label'] = "Number of Households"
        return context

    @classmethod
    def prepare_color_range(cls, city_ids):
        queryset = CommunityHousingDevelopmentFund.objects.filter(
            loan_status="Disbursed"
        ).values('city_id').annotate(number_of_households_received_housing_loan=Count('id'))

        color_dict = dict()
        color_dict['city_range'] = ['> 0', ]
        for city in city_ids:
            color_dict[city] = 0  # default color range

        if queryset.exists():
            _key = 'number_of_households_received_housing_loan'
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
        queryset = CommunityHousingDevelopmentFund.objects.filter(
            loan_status="Disbursed"
        ).values('city_id').annotate(number_of_households_received_housing_loan=Count('id'))

        total_key = 'Households'
        result = dict()
        for city in city_ids:
            result[city] = {
                total_key: 0
            }

        for _item in queryset:
            result[_item['city_id']][total_key] = _item['number_of_households_received_housing_loan'] or 0

        return result

    @classmethod
    def prepare_housing_loan_data(cls, city_ids=None):
        queryset = CommunityHousingDevelopmentFund.objects.filter(city__isnull=False, loan_status="Disbursed")
        if city_ids:
            queryset = queryset.filter(city__in=city_ids)
            geography_ids = city_ids
        else:
            geography_ids = list(Geography.objects.filter(
                level__name='Pourashava/City Corporation'
            ).values_list('pk', flat=True))

        result = dict()
        _key = 'Number of Households Received Housing Loan'
        for geography_id in geography_ids:
            result[geography_id] = {
                _key: 0,
            }

        _queryset = queryset.values('city_id').annotate(number_of_households_received_housing_loan=Count(F('id')))

        for _item in _queryset:
            number_of_households = _item['number_of_households_received_housing_loan'] or 0
            result[_item['city_id']][_key] = number_of_households

        return result

    def get_json_response(self, content, **kwargs):
        city_ids = self.str_to_list(self.extract_parameter('city'))

        data_dict = dict()
        data_dict['title'] = "Number of Households Received Housing Loan from CHDF"
        data_dict['data'] = self.prepare_housing_loan_data(city_ids)

        return super(CHDFLoanMapReportView, self).get_json_response(
            self.convert_context_to_json(data_dict), **kwargs)
