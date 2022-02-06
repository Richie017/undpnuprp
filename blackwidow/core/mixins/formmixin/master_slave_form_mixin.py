from django import forms
from django.forms.utils import ErrorList

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.contracts.base import DomainEntity

__author__ = 'mahmudul'


class GenericMasterSlaveFormMixin(GenericFormMixin):
    parent_id = forms.CharField(widget=forms.HiddenInput, required=True)

    parent_instance = None
    parent_model = DomainEntity
    child_instances = None

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, **kwargs):
        super().__init__(data=data, files=files, auto_id=auto_id, prefix=prefix, initial=initial, error_class=error_class, label_suffix=label_suffix, empty_permitted=empty_permitted, **kwargs)

        self.fields['parent_id'].initial = kwargs.get('parent_id')
        self.parent_instance = self.parent_model.objects.get(pk=kwargs.get('parent_id'))

        if 'ids' in kwargs['request'].GET:
            ids = kwargs['request'].GET['ids'].split(',')
            self.child_instances = self.Meta.model.objects.filter(pk__in=ids)
