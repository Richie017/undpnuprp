from django import forms
from django.db import transaction

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin import GenericFormMixin
from blackwidow.core.models import Geography
from undp_nuprp.nuprp_admin.models import DeleteTestSurvey


class DeleteTestSurveyForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(DeleteTestSurveyForm, self).__init__(data=data, files=files, instance=instance,
                                                   prefix=prefix, **kwargs)

        self.fields['city'] = GenericModelChoiceField(
            required=True,
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation').order_by('name'),
            label='City',
            empty_label='Select One',
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'}))

        self.fields['from_date'] = forms.DateTimeField(
            input_formats=['%d/%m/%Y'],
            required=True,
            label='From Date',
            widget=forms.DateTimeInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker'
                },
                format='%d/%m/%Y'
            ),
        )
        self.fields['to_date'] = forms.DateTimeField(
            input_formats=['%d/%m/%Y'],
            label='To Date',
            required=True,
            widget=forms.DateTimeInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker'
                },
                format='%d/%m/%Y'
            ),
        )

    def save(self, commit=True):
        with transaction.atomic():
            self.instance = super().save(commit)
            self.instance.status = 'Scheduled'
            self.instance.save()

    class Meta:
        model = DeleteTestSurvey
        fields = ('city', 'from_date', 'to_date')
