from datetime import date

from django import forms

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.models import Geography
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.models import MonthlyTarget
from undp_nuprp.approvals.models.target_and_progress.monthly_target_and_progress.citywise_monthly_target import \
    CityWiseMonthlyTarget
from undp_nuprp.approvals.utils.month_enum import MonthEnum
from undp_nuprp.approvals.views.target_and_progress.target_base import TargetBaseView

__author__ = 'Ziaul Haque'


@decorate(override_view(model=MonthlyTarget, view=ViewActionEnum.Manage))
class MonthlyTargetView(TargetBaseView):
    def get_template_names(self):
        return ['target_and_progress/monthly_target.html']

    def get_search_parameters(self):
        parameters = super(MonthlyTargetView, self).get_search_parameters()
        today = date.today()
        year_choices = tuple()
        for y in range(2000, 2100):
            year_choices += ((y, str(y)),)

        quarter_choices = tuple()
        for _choice, _quarter in enumerate(MonthlyTarget.get_quarters()):
            quarter_choices += ((_choice + 13, _quarter),)

        output_choices = tuple()
        outputs = CityWiseMonthlyTarget.objects.values_list('output', flat=True).order_by('output').distinct()

        for output in outputs:
            output_choices += ((output, output),)

        parameters['G1'] = self.get_wrapped_parameters((
            {
                'name': 'city',
                'field': GenericModelChoiceField(
                    queryset=Geography.objects.filter(level__name='Pourashava/City Corporation'),
                    label='Select City',
                    empty_label=None,
                    required=False,
                    widget=forms.Select(
                        attrs={
                            'class': 'select2',
                            'width': '220',
                            'multiple': 'multiple',
                        }
                    )
                )
            },
        ))
        parameters['G2'] = self.get_wrapped_parameters((
            {
                'name': 'output',
                'field': forms.ChoiceField(
                    label='Select Output',
                    choices=output_choices,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220', 'multiple': 'multiple'}
                    )
                )
            },
            {
                'name': 'quarter',
                'field': forms.ChoiceField(
                    choices=quarter_choices,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    )
                )
            },
        ))
        parameters['G3'] = self.get_wrapped_parameters((
            {
                'name': 'year',
                'field': forms.ChoiceField(
                    choices=year_choices,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    ), initial=today.year
                )
            },
            {
                'name': 'month',
                'field': forms.ChoiceField(
                    choices=MonthEnum.get_choices(),
                    initial=today.month,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    )
                )
            },
        ))
        parameters['G4'] = self.get_wrapped_parameters((
        ))
        return parameters

    def get_json_response(self, content, **kwargs):
        city_param = self.extract_parameter('city')
        output_param = self.extract_parameter('output')
        month_param = self.extract_parameter('month')
        year_param = self.extract_parameter('year')
        quarter_param = self.extract_parameter('quarter')

        city_ids = None
        outputs = output_param.split(',') if output_param else None

        if city_param:
            city_ids = [int(x) for x in city_param.split(',')]

        today = date.today()
        if month_param:
            month = int(month_param)
        else:
            month = today.month

        if year_param:
            year = int(year_param)
        else:
            year = today.year

        quarter = int(quarter_param)

        headers = self.model.header_columns(month=month, year=year, quarter=quarter)

        data_dict = dict()
        data_dict['headers'] = headers
        data_dict['header_widths'] = [7, 7, 7, 12, 7, 12, 12, 8, 7, 7, 7, 7]
        data_dict['data_rows'] = self.model.get_target_data_rows(
            month=month, year=year, city_ids=city_ids, outputs=outputs, quarter=quarter_param
        )

        return super(MonthlyTargetView, self).get_json_response(self.convert_context_to_json(data_dict), **kwargs)
