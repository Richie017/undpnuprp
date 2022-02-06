from django import forms

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.approvals.models.infrastructures.base.completed_contract import CompletedContract

__author__ = 'Shuvro'

Yes_No_Choices = (('', 'Select One'), ('Yes', 'Yes'), ('No', 'No'),)


class CompletedContractForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(CompletedContractForm, self).__init__(data=data, files=files, instance=instance,
                                                    prefix=prefix, **kwargs)
        self.fields['completed_as_expected_date'] = forms.ChoiceField(
            required=False,
            label='Completed as per expected end date?',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.completed_as_expected_date if instance and instance.pk else None
        )
        self.fields['number_of_days_overrun'].label = 'Number of days overrun (including weekends)?'

        self.fields['within_budget'] = forms.ChoiceField(
            required=False,
            label='Within budget?',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.within_budget if instance and instance.pk else None
        )

        self.fields['amount_deposited_to_om_fund'].label = 'Amount deposited to O&M fund'

        self.fields['variation_order'] = forms.ChoiceField(
            required=False,
            label='Variation order',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.variation_order if instance and instance.pk else None
        )
        self.fields['post_survey_date'] = forms.DateTimeField(
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            required=False,
            initial=instance.post_survey_date if instance and instance.pk else None
        )
        self.fields['om_Fund_established_date'] = forms.DateTimeField(
            label='O&M Fund Established Date',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            required=False,
            initial=instance.om_Fund_established_date if instance and instance.pk else None
        )

    class Meta(GenericFormMixin.Meta):
        model = CompletedContract
        fields = ('completed_as_expected_date', 'number_of_days_overrun',
                  'number_of_people_employed', 'total_number_of_person_days', 'within_budget',
                  'amount_of_budget_overrun', 'amount_deposited_to_om_fund',
                  'post_survey_date', 'project_completion_report',
                  'project_handover', 'om_Fund_established_date',
                  'variation_order', 'what_kind_of_changes')
        labels = {
            'what_kind_of_changes': 'What kind of changes (qualitative information)'
        }
