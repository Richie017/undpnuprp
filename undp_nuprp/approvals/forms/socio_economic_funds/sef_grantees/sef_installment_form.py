from django import forms

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.approvals.models import SEFInstallment

__author__ = 'Ziaul Haque'


class SEFInstallmentForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SEFInstallmentForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)
        self.fields['installment_date'] = \
            forms.DateTimeField(
                label='Date instalment received by grantee',
                input_formats=['%d/%m/%Y'],
                widget=forms.DateTimeInput(
                    attrs={'data-format': "dd/MM/yyyy", 'class': 'date-time-picker', 'readonly': 'True'},
                    format='%d/%m/%Y'
                )
            )

    def clean(self):
        return super(SEFInstallmentForm, self).clean()

    class Meta(GenericFormMixin.Meta):
        model = SEFInstallment
        fields = ('installment_id', 'installment_value', 'installment_date')
        labels = {
            'installment_id': 'Instalment number',
            'installment_value': 'Value of instalment',
            'installment_date': 'Date instalment received by grantee'
        }
