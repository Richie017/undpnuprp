from django import forms

from blackwidow.core.forms.common.contact_address_form import ContactAddressForm
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc_cluster import CDCCluster


__author__ = "Shama"


class CDCClusterForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        kwargs.update({'address_level': 'Pourashava/City Corporation'})
        super().__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)
        self.add_child_form('address', ContactAddressForm(data=data, files=files, form_header='Address',
                                                          instance=self.instance.address if self.instance.pk else None,
                                                          **kwargs))

        self.fields['remarks'] = forms.CharField(
            label='Type',
            widget=forms.Select(choices=[('', 'Select One'), ('Old', 'Old'), ('New', 'New')],
                                attrs={'class': 'select2', 'width': '220'}))

        self.fields['assigned_code'] = forms.CharField(
            label='Cluster ID',
            required=False
        )

        self.fields['date_of_formation'] = forms.DateTimeField(
            label='Date of Formation',
            input_formats=['%d/%m/%Y %H:%M'],
            required=False,
            widget=forms.DateTimeInput(
                attrs={
                    'data-format': "dd/MM/yyyy hh:mm",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y %H:%M'
            ),
        )

    class Meta(GenericFormMixin.Meta):
        model = CDCCluster
        fields = ('name', 'remarks', 'assigned_code', 'date_of_formation')