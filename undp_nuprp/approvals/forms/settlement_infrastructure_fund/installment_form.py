from django import forms

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.approvals.models.infrastructures.base.installment import SIFInstallment

__author__ = 'Shuvro'


class SIFInstallmentForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SIFInstallmentForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['installment_number'].label = 'Instalment number'
        self.fields['installment_number'].required = False
        self.fields['installment_value'].label = 'Value of instalment'
        self.fields['installment_value'].required = False
        self.fields['installment_date'] = forms.DateTimeField(
            label='Date of instalment',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.installment_date if instance and instance.pk else None
        )
        self.fields['installment_date'].required = False
        self.fields['status_of_physical_progress'].required = False
        self.fields['status_of_financial_progress'].required = False

    class Meta(GenericFormMixin.Meta):
        model = SIFInstallment
        fields = ('installment_number', 'installment_value', 'installment_date', 'status_of_physical_progress',
                  'status_of_financial_progress')

        labels = {
            'status_of_physical_progress': 'Status of physical Progress (descriptive)',
            'status_of_financial_progress': 'Status of Financial Progress %'
        }
