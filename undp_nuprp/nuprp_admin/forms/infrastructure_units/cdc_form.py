from django import forms
from django.urls.base import reverse
from django.db import transaction
from django.db.models.functions import Length

from blackwidow.core.forms.common.contact_address_form import ContactAddressForm
from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.geography.geography import Geography
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc import CDC
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc_cluster import CDCCluster

__author__ = "Shama"


class CDCForm(GenericFormMixin):
    city = forms.IntegerField()

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        kwargs.update({'address_level': 'Ward'})
        super().__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)
        self.add_child_form('address',
                            ContactAddressForm(data=data, files=files, form_header='Address', prefix='address',
                                               instance=self.instance.address if self.instance.pk else None,
                                               **kwargs))

        self.fields['remarks'] = forms.CharField(
            label='Type',
            widget=forms.Select(choices=[('', 'Select One'), ('Old', 'Old'), ('New', 'New')],
                                attrs={'class': 'select2', 'width': '220'}))

        self.fields['city'] = GenericModelChoiceField(
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation').order_by('name'), label='City',
            empty_label='Select One',
            initial=instance.address.geography.parent if instance is not None else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'}))

        self.fields['parent'] = GenericModelChoiceField(
            queryset=CDCCluster.objects.all(), label='CDC Cluster',
            initial=instance.parent if instance is not None else None,
            widget=forms.TextInput(attrs={'class': 'select2-input', 'width': '220',
                                          'data-depends-on': 'city',
                                          'data-depends-property': 'address:geography:id',
                                          'data-url': reverse(CDCCluster.get_route_name(
                                              ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1&sort=name'
                                          }))

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

    def save(self, commit=True):
        with transaction.atomic():
            self.instance = super(CDCForm, self).save(commit)
            if self.instance.assigned_code is None or self.instance.assigned_code == '':
                ward_code = self.instance.address.geography.name
                city_code = self.instance.address.geography.parent.short_code
                cdc_number = CDC.all_objects.annotate(code_len=Length('assigned_code')).filter(
                    address__geography__pk=self.instance.address.geography.pk, code_len=8).count()
                if len(ward_code) < 2:
                    ward_code = '0' + ward_code
                if len(city_code) < 3:
                    city_code = '0' + city_code
                cdc_serial = str((cdc_number + 1) % 1000)
                if len(cdc_serial) <= 2:
                    cdc_serial = cdc_serial.zfill(3)
                self.instance.assigned_code = '%3s%2s%3s' % (city_code, ward_code, cdc_serial)
                self.instance.save()
            else:
                pass
            return self.instance

    class Meta(GenericFormMixin.Meta):
        model = CDC
        fields = ('name', 'remarks', 'city', 'parent', 'date_of_formation')
