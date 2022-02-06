from django import forms
from django.db import transaction

from blackwidow.core.forms.common.contact_address_form import ContactAddressForm
from blackwidow.core.forms.common.phone_number_form import PhoneNumberForm
from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.clients.client import Client
from blackwidow.core.models.finanical.financial_information import FinancialInformation
from blackwidow.core.models.manufacturers.manufacturer import Manufacturer

__author__ = 'Mahmud'


class ClientForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super().__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)
        _prefix = prefix
        if _prefix != '':
            _prefix += '-'

        if 'manufacturer' in self.fields:
            self.fields['manufacturer'] = GenericModelChoiceField(
                queryset=Manufacturer.objects.all(), widget=forms.Select(attrs={'class': 'select2'}))
        self.add_child_form(
            "address", ContactAddressForm(
                data=data, files=files, instance=instance.address if instance is not None else None,
                form_header='Address', prefix=_prefix + str(len(self.suffix_child_forms)), **kwargs))
        self.add_child_form(
            "phone_number", PhoneNumberForm(
                data=data, files=files, instance=instance.phone_number if instance is not None else None,
                form_header='Phone Number', prefix=_prefix + str(len(self.suffix_child_forms)), **kwargs))

    def save(self, commit=True):
        with transaction.atomic():
            if self.instance.financial_information is None:
                fi = FinancialInformation()
                fi.save()
                self.instance.financial_information = fi
            self.instance.available_credit = self.instance.credit_limit
            return super().save(commit)

    class Meta:
        model = Client
        fields = ['name', 'assigned_to', 'qr_code']
