from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.common.custom_field import CustomFieldValue

__author__ = 'Tareq'


class CustomFieldValueForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, **kwargs):
        super().__init__(data=data, files=files, instance=instance, **kwargs)

    class Meta:
        model = CustomFieldValue
        fields = []
