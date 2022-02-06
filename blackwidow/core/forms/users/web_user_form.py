from blackwidow.core.forms.common.contact_address_form import ContactAddressForm
from blackwidow.core.forms.common.email_address_form import EmailAddressForm
from blackwidow.core.forms.common.phone_number_form import PhoneNumberForm
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.users.web_user import WebUser

__author__ = 'Mahmud'


class WebUserForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', form_header='', **kwargs):
        super().__init__(data=data, files=files, instance=instance, prefix=prefix, form_header=form_header, **kwargs)
        self.add_child_form("email", EmailAddressForm(data, files, form_header=form_header + ' - ' + 'Email',
                                                      instance=instance.email if instance is not None else None,
                                                      display_inline=True, **kwargs))
        self.add_child_form("phone", PhoneNumberForm(data, files, form_header=form_header + ' - ' + 'Phone',
                                                     instance=instance.phone if instance is not None else None,
                                                     display_inline=True, **kwargs))
        self.add_child_form("address", ContactAddressForm(data, files, form_header=form_header + ' - ' + 'Address',
                                                          instance=instance.address if instance is not None else None,
                                                          display_inline=True, **kwargs))

    class Meta(GenericFormMixin.Meta):
        model = WebUser
        fields = ['name', 'designation']
        labels = {
            'name': 'Full Name'
        }
