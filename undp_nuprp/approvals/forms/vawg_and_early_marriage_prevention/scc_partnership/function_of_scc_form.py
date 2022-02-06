from django import forms

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.approvals.models.vawg_and_early_marriage_prevention.functioning_of_scc import FunctionOfSCC

Yes_No_Choices = (('', 'Select One'), ('Yes', 'Yes'), ('No', 'No'),)


class FunctionOfSCCForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(FunctionOfSCCForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['number_of_male'].required = False
        self.fields['number_of_female'].required = False
        self.fields['number_of_disabled'].required = False
        self.fields['number_of_disabled_male'].required = False
        self.fields['number_of_disabled_female'].required = False
        self.fields['number_of_transsexual'].required = False
        self.fields['number_of_participants'].required = False
        self.fields['how_many_scc_bi_annual_meeting_held_till_date'].required = False
        self.fields['number_of_participants'].widget.attrs['readonly'] = True

        self.fields['any_scc_bi_annual_meeting_held_till_date'] = forms.ChoiceField(
            label='Any SCC bi-annual meeting held till date?',
            required=False,
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'}
            ),
            initial=instance.any_scc_bi_annual_meeting_held_till_date if instance and instance.pk else None
        )

        self.fields['scc_last_hold_its_quarterly_review_meeting'] = forms.DateTimeField(
            required=False,
            label='When did the SCC last hold it\'s bi-annual (review) meeting?',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.scc_last_hold_its_quarterly_review_meeting if instance and instance.pk else None
        )

        self.fields['parts_of_the_scc_plan_included_within_the_cap'] = forms.ChoiceField(
            label='Are parts of the SCC plan included within the CAP?',
            required=False,
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'}
            ),
            initial=instance.parts_of_the_scc_plan_included_within_the_cap if instance and instance.pk else None
        )

    class Meta:
        model = FunctionOfSCC
        fields = 'any_scc_bi_annual_meeting_held_till_date', 'how_many_scc_bi_annual_meeting_held_till_date', \
                 'scc_last_hold_its_quarterly_review_meeting', 'number_of_male', 'number_of_female', \
                 'number_of_disabled', 'number_of_disabled_male', 'number_of_disabled_female', 'number_of_transsexual', \
                 'number_of_participants', 'parts_of_the_scc_plan_included_within_the_cap'
        labels = {
            'how_many_scc_bi_annual_meeting_held_till_date': 'How many SCC bi-annual meeting held till date?',
            'number_of_disabled_male': 'Number of disabled (Male)',
            'number_of_disabled_female': 'Number of disabled (Female)'
        }
