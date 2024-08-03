from blackwidow.core.forms.common.contact_address_form import ContactAddressForm
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.nuprp_admin.models.infrastructure_units.household import Household

__author__ = 'Tareq'


class HouseholdForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super().__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)
        self.add_child_form('address', ContactAddressForm(data=data, files=files, form_header='Address',
                                                          instance=self.instance.address if self.instance.pk else None,
                                                          **kwargs))

    class Meta(GenericFormMixin.Meta):
        model = Household
        fields = 'name',
