from django import forms
from django.db import transaction

from blackwidow.core.mixins.formmixin import GenericMasterSlaveFormMixin
from blackwidow.core.models import Role
from blackwidow.core.models.common.custom_field import CustomField
from blackwidow.engine.exceptions import EntityNotEditableException

__author__ = 'Tareq'


class CustomFieldForm(GenericMasterSlaveFormMixin):
    parent_model = Role

    def __init__(self, data=None, files=None, form_header='', instance=None, prefix='', **kwargs):
        super().__init__(data=data, files=files, form_header=form_header, instance=instance, prefix=prefix, **kwargs)

    def delete(self, commit=True):
        if self.request.c_user.role.id == self.parent_instance.id:
            raise EntityNotEditableException("You cannot edit permissions for your own role.")
        with transaction.atomic():
            parent = self.parent_instance
            for c_field in self.child_instances:
                parent.custom_fields.remove(c_field)
            parent.save(commit)

    def save(self, commit=True):
        if self.request.c_user.role.id == self.parent_instance.id:
            raise EntityNotEditableException("You cannot edit permissions for your own role.")
        with transaction.atomic():
            c_field = super().save(commit)
            parent = self.parent_instance
            for x in filter(lambda a: a.name == c_field.name, parent.custom_fields.all()):
                parent.custom_fields.remove(x)
            parent.custom_fields.add(c_field)
            parent.save(commit)
            return c_field

    class Meta(GenericMasterSlaveFormMixin.Meta):
        model = CustomField
        fields = ['name', 'field_type', 'is_required', 'list_values']
        widgets = {
            'field_type': forms.Select(attrs={'class': 'select2 toggle_choices'}),
            'list_values': forms.Textarea(attrs={'class': 'select2'})
        }

        labels = {
            'field_type': 'Field Type',
            'is_required': 'Is Required',
            'list_values': 'Choices'
        }
