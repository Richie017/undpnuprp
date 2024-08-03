from blackwidow.core.forms.common.contact_address_form import ContactAddressForm
from blackwidow.core.forms.common.phone_number_form import PhoneNumberForm
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.stores.store import Store


__author__ = 'Mahmud'


class StoreForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super().__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)
        _prefix = prefix
        if _prefix != '':
            _prefix += '-'
        else:
            _prefix = 'suffix-'
            
        # self.add_child_form("contact_person", WebUserForm(data=data, files=files, form_header='Contact Person', instance=instance.contact_person if instance is not None else None, prefix=_prefix + str(len(self.suffix_child_forms)), **kwargs))
        self.add_child_form("address", ContactAddressForm(data=data, files=files, form_header='Address', instance=instance.address if instance is not None else None, prefix=_prefix + str(len(self.suffix_child_forms)), **kwargs))
        self.add_child_form("phone_number", PhoneNumberForm(data=data, files=files, form_header='Phone Number', instance=instance.phone_number if instance is not None else None, prefix=_prefix + str(len(self.suffix_child_forms)), **kwargs))

    class Meta:
        model = Store
        fields = ['name']