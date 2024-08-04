from django.db import transaction

from blackwidow.core.forms.common.contact_address_form import ContactAddressForm
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.common.custom_field import CustomFieldValue
from blackwidow.core.models.structure.warehouse import WareHouse
from blackwidow.engine.extensions import bw_titleize
from blackwidow.engine.extensions.generate_form_fields import genarate_form_field


class WareHouseForm(GenericFormMixin):

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super().__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        prefix = prefix + '-' if prefix != '' else prefix
        self.add_child_form("address", ContactAddressForm(data=data, files=files, form_header='Address', instance=instance.address if instance is not None else None, **kwargs))
        kwargs.update({
            'prefix': 'meta'
        })
        if self.instance is not None and self.instance.pk is not None:
            custom_fields = self.instance.custom_fields.all()
        else:
            custom_fields = CustomFieldValue.objects.none()
        custom_field_form = self
        _index = 0
        for x in self.Meta.model.get_default_custom_field_list():
            field_instance_args = {
                'label': bw_titleize(x.name),
                'required': x.is_required,
                }
            custom_field_form.fields['field_' + str(_index)] = genarate_form_field(x, field_instance_args)
            if x.name not in [f.field.name for f in custom_fields]:
                custom_field_form.fields['field_' + str(_index)].initial = ""
            else:
                custom_field_form.fields['field_' + str(_index)].initial = [f.value for f in custom_fields if f.field.name == x.name][0]
            _index += 1

    def save(self, commit=True):
        with transaction.atomic():
            super().save(commit=commit)

            self.instance.custom_fields.clear()
            custom_field_form = self
            index = 0
            for x in self.Meta.model.get_default_custom_field_list():
                if ('field_' + str(index)) in custom_field_form.fields:
                    value = custom_field_form.cleaned_data['field_' + str(index)]
                else:
                    value = ""
                f_value = CustomFieldValue()
                f_value.organization = self.instance.organization
                f_value.value = value
                f_value.field = x
                f_value.save()
                self.instance.custom_fields.add(f_value)
                index += 1

            return self.instance

    class Meta:
        model = WareHouse
        fields = ['name']