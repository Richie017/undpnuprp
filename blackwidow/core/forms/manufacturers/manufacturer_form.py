from django.forms.models import modelformset_factory

from blackwidow.core.forms.common.contact_address_form import ContactAddressForm
from blackwidow.core.forms.common.email_address_form import EmailAddressForm
from blackwidow.core.forms.common.phone_number_form import PhoneNumberForm
from blackwidow.core.forms.users.web_user_form import WebUserForm
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin, GenericModelFormSetMixin
from blackwidow.core.models.common.contactaddress import ContactAddress
from blackwidow.core.models.common.emailaddress import EmailAddress
from blackwidow.core.models.common.phonenumber import PhoneNumber
from blackwidow.core.models.manufacturers.manufacturer import Manufacturer
from blackwidow.core.models.users.web_user import WebUser

__author__ = 'Mahmud'

web_user_form_set = modelformset_factory(WebUser, form=WebUserForm, formset=GenericModelFormSetMixin, extra=0,
                                         min_num=1, validate_min=False)
address_form_set = modelformset_factory(ContactAddress, form=ContactAddressForm, formset=GenericModelFormSetMixin,
                                        extra=0, min_num=1, validate_min=False)
email_form_set = modelformset_factory(EmailAddress, form=EmailAddressForm, formset=GenericModelFormSetMixin, extra=0,
                                      min_num=1, validate_min=False)
phone_number_form_set = modelformset_factory(PhoneNumber, form=PhoneNumberForm, formset=GenericModelFormSetMixin,
                                             extra=0, min_num=1, validate_min=False)


class ManufacturerForm(GenericFormMixin):
    def __init__(self, data=None, files=None, prefix='', instance=None, **kwargs):
        super().__init__(data=data, files=files, prefix=prefix, instance=instance, **kwargs)
        prefix = prefix + '-' if prefix != '' else prefix
        self.add_child_form("contact_persons", web_user_form_set(data=data,
                                                                 queryset=instance.contact_persons.all() if instance is not None else WebUser.objects.none(),
                                                                 files=files, header='Contact Person',
                                                                 prefix=prefix + 'suffix-' + str(
                                                                     len(self.suffix_child_forms)), **kwargs))
        self.add_child_form("addresses", address_form_set(data=data,
                                                          queryset=instance.addresses.all() if instance is not None else ContactAddress.objects.none(),
                                                          files=files, header='Address',
                                                          prefix=prefix + 'suffix-' + str(len(self.suffix_child_forms)),
                                                          **kwargs))
        self.add_child_form("emails", email_form_set(data=data,
                                                     queryset=instance.emails.all() if instance is not None else EmailAddress.objects.none(),
                                                     files=files, header='Email',
                                                     prefix=prefix + 'suffix-' + str(len(self.suffix_child_forms)),
                                                     **kwargs))
        self.add_child_form("phone_numbers", phone_number_form_set(data=data,
                                                                   queryset=instance.phone_numbers.all() if instance is not None else PhoneNumber.objects.none(),
                                                                   files=files, header='Phone',
                                                                   prefix=prefix + 'suffix-' + str(
                                                                       len(self.suffix_child_forms)), **kwargs))

    class Meta(GenericFormMixin.Meta):
        model = Manufacturer
        fields = ['name', 'discount', 'is_master']
        labels = {
            'discount': 'Discount (%)'
        }
