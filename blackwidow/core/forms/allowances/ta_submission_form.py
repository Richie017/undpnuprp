from django import forms

from blackwidow.core.forms.common.location_form import LocationForm
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.allowances.transport_allowance import TransportAllowance


__author__ = 'ruddra'


class TASubmissionForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, form_header= None, prefix='', **kwargs):
        super().__init__(data=data, files=files,form_header= "Transport Allowances", instance=instance, **kwargs)
        # _prefix = kwargs.get('prefix', '')
        if prefix != '':
            prefix += '-'
            
        self.fields['transport_type'] = forms.ChoiceField(choices=(
            ('Bus', 'Bus'),
            ('CNG', 'CNG'),
        ), widget=forms.Select(attrs={'class': 'select2'}))
        kwargs.update({
            'prefix': prefix + 'location'
        })
        self.add_child_form("location", LocationForm(data, files, form_header='Location', instance=instance.location if instance is not None else None, **kwargs))

    class Meta:
        model = TransportAllowance
        fields = ['transport_type', 'fair']
