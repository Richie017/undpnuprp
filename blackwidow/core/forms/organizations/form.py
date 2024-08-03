from django.db import transaction
from django.forms.models import modelformset_factory

from blackwidow.core.forms.common.contact_address_form import ContactAddressForm
from blackwidow.core.forms.common.email_address_form import EmailAddressForm
from blackwidow.core.forms.common.phone_number_form import PhoneNumberForm
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin, GenericModelFormSetMixin
from blackwidow.core.models.common.contactaddress import ContactAddress
from blackwidow.core.models.common.emailaddress import EmailAddress
from blackwidow.core.models.common.phonenumber import PhoneNumber
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.engine.extensions.clock import Clock

__author__ = 'ruddra'

from django import forms

emailaddess_formset = modelformset_factory(EmailAddress, form=EmailAddressForm, formset=GenericModelFormSetMixin, extra=0, min_num=1)
phonenumber_formset = modelformset_factory(PhoneNumber, form=PhoneNumberForm, formset=GenericModelFormSetMixin, extra=0, min_num=1)
contactaddess_formset = modelformset_factory(ContactAddress, form=ContactAddressForm, formset=GenericModelFormSetMixin, extra=0, min_num=1)

class OrganizationForm(GenericFormMixin):
    date_joined = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M:%S'], widget=forms.DateTimeInput(attrs={'data-format':"dd/MM/yyyy hh:mm:ss", 'class': 'date-time-picker', 'readonly': 'True'}, format='%d/%m/%Y %H:%M:%S'))
    registration_date = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M:%S'], widget=forms.DateTimeInput(attrs={'data-format':"dd/MM/yyyy hh:mm:ss", 'class': 'date-time-picker', 'readonly': 'True'}, format='%d/%m/%Y %H:%M:%S'))

    def __init__(self, data=None, files=None, instance=None, prefix='', form_header='',  **kwargs):
        super().__init__(data=data, files=files, instance=instance, prefix=prefix, form_header=form_header,  **kwargs)
        if instance and instance.date_joined:
            self.fields['date_joined'].initial = Clock.get_user_local_time(instance.date_joined)
        if instance and instance.registration_date:
            self.fields['registration_date'].initial = Clock.get_user_local_time(instance.registration_date)
        self.add_child_form("emails", emailaddess_formset(data=data, files=files, header='Emails', prefix= prefix + str(len(self.suffix_child_forms)), queryset=EmailAddress.objects.none() if not instance else instance.emails.all(), add_more=True, **kwargs))
        self.add_child_form("phones", phonenumber_formset(data=data, files=files, header='Phones', prefix= prefix + str(len(self.suffix_child_forms)), queryset=PhoneNumber.objects.none() if not instance else instance.phones.all(), add_more=True, **kwargs))
        self.add_child_form("addresses", contactaddess_formset(data=data, files=files, header='Company Address', prefix= prefix + str(len(self.suffix_child_forms)), queryset=ContactAddress.objects.none() if not instance else instance.addresses.all(), add_more=True, **kwargs))

    def save(self, commit=True):
        with transaction.atomic():
            self.instance.registration_date = (self.cleaned_data['registration_date']).timestamp() * 1000
            self.instance.date_joined = (self.cleaned_data['date_joined']).timestamp() * 1000
            return super().save(commit)

    class Meta(GenericFormMixin.Meta):
        model = Organization
        fields = ['name', 'trade_license_number']



