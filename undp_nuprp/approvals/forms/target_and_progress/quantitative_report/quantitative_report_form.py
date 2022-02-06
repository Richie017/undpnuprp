from datetime import date

from django import forms

from blackwidow.core.forms import FileObjectForm
from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models import Geography
from undp_nuprp.approvals.models import QuantitativeReport
from undp_nuprp.approvals.utils.month_enum import MonthEnum

__author__ = 'Ziaul Haque'


class QuantitativeReportForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(QuantitativeReportForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)
        today = date.today()
        year_choices = tuple()
        for y in range(2000, 2100):
            year_choices += ((y, str(y)),)

        self.fields['city'] = \
            GenericModelChoiceField(
                queryset=Geography.objects.filter(level__name='Pourashava/City Corporation'),
                label='City',
                widget=forms.Select(
                    attrs={
                        'class': 'select2',
                        'width': '220',
                    }
                )
            )

        self.fields['year'] = forms.ChoiceField(
            choices=year_choices,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}
            ), initial=today.year
        )

        self.fields['month'] = forms.ChoiceField(
            label='Reporting Month',
            choices=MonthEnum.get_choices(),
            initial=today.month,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}
            )
        )

        self.fields['submission_date'] = \
            forms.DateTimeField(
                label='Date of Submission',
                input_formats=['%d/%m/%Y'],
                initial=today.strftime('%d/%m/%Y'),
                widget=forms.DateTimeInput(
                    attrs={'data-format': "dd/MM/yyyy", 'readonly': 'True'},
                    format='%d/%m/%Y'
                )
            )

        self.add_child_form("attached_file", FileObjectForm(
            data=data, files=files, instance=instance.attached_file if instance else None,
            form_header='Attached File', **kwargs))

    class Meta(GenericFormMixin.Meta):
        model = QuantitativeReport
        fields = ('city', 'year', 'month', 'submission_date')
