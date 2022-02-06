from datetime import date

from django import forms

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin import GenericFormMixin
from blackwidow.core.models import Geography
from undp_nuprp.nuprp_admin.models.citizen_participation_and_community_mobilization.cdc_assessment import CDCAssessment

__author__ = "Ziaul Haque"

YEAR_CHOICES = tuple()
YEAR_CHOICES += (('', "Select One"),)
for year in range(2000, 2101):
    YEAR_CHOICES += ((year, str(year)),)


class CDCAssessmentForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(CDCAssessmentForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['city'] = GenericModelChoiceField(
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation'),
            initial=instance.city if instance and instance.pk else None,
            label='City',
            empty_label='Select One',
            required=False,
            widget=forms.Select(
                attrs={
                    'class': 'select2',
                    'width': '220',
                }
            )
        )

        self.fields['year'] = forms.ChoiceField(
            choices=YEAR_CHOICES, required=False,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}
            ), initial=date.today().year
        )

    class Meta(GenericFormMixin.Meta):
        model = CDCAssessment

        fields = [
            'year', 'city', 'number_of_cdc', 'ward_no', 'fully_effective',
            'moderately_effective', 'weak', 'very_weak'
        ]

        labels = {
            'number_of_cdc': 'Number of CDC'
        }

    def save(self, commit=True):
        if len(self.cleaned_data['ward_no']) == 1:
            self.instance.ward_no = "0" + str(self.cleaned_data['ward_no'])
        return super(CDCAssessmentForm, self).save(commit=commit)

