from django import forms

from blackwidow.core.forms.common.location_form import LocationForm
from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.clients.client import Client
from blackwidow.core.models.clientvisit.client_visit import VisitClient

__author__ = 'activehigh'


class VisitClientForm(GenericFormMixin):

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super().__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)
        self.fields['client'] = GenericModelChoiceField(queryset=Client.objects.all(), widget=forms.Select(attrs={'class':'select2'}))
        self.add_child_form('location', LocationForm(data=data, files=files, instance=instance.location if instance is not None else None, prefix=prefix + str(len(self.suffix_child_forms))))

    class Meta:
        model = VisitClient
        fields = ['client', 'description']
        # labels = {
        #     'client': 'Aparajita / Distributor'
        # }
        # widgets = {
        #     'client': forms.Select(attrs={'class': 'select2'}),
        #     'description': forms.Textarea(attrs={'class': 'description'})
        # }
