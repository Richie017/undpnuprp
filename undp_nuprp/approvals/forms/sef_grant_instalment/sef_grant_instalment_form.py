from django import forms

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.approvals.models.sef_grant_disbursement.sef_grant_instalment import SEFGrantInstalment

__author__ = 'Shuvro'


class SEFGrantInstalmentForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SEFGrantInstalmentForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)
        self.fields['date'] = \
            forms.DateTimeField(
                input_formats=['%d/%m/%Y'],
                required=False,
                widget=forms.DateTimeInput(
                    attrs={'data-format': "dd/MM/yyyy", 'class': 'date-time-picker', 'readonly': 'True'},
                    format='%d/%m/%Y'
                )
            )

    class Meta(GenericFormMixin.Meta):
        model = SEFGrantInstalment
        fields = ('number', 'value', 'status', 'date')
        # labels = {
        #     'number': 'Instalment number',
        #     'value': 'Value of instalment',
        #     'status': 'Status of instalment',
        #     'date': 'Date instalment'
        # }
