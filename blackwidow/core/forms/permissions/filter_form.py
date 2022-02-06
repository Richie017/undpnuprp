from django import forms
from django.db import transaction
from django.forms.utils import ErrorList

from blackwidow.core.mixins.formmixin.master_slave_form_mixin import GenericMasterSlaveFormMixin
from blackwidow.core.models.permissions.query_filter import QueryFilter
from blackwidow.core.models.roles.role import Role
from blackwidow.engine.decorators.utility import get_models_with_decorator
from blackwidow.engine.exceptions.exceptions import EntityNotEditableException
from blackwidow.engine.extensions import bw_titleize
from config.apps import INSTALLED_APPS

__author__ = 'mahmudul'


class QueryFilterForm(GenericMasterSlaveFormMixin):
    context = forms.ChoiceField(label='Select context', widget=forms.Select(attrs={'class': 'select2'}), required=False,
                                initial=1)
    parent_model = Role

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, **kwargs):
        super().__init__(data=data, files=files, auto_id=auto_id, prefix=prefix, initial=initial,
                         error_class=error_class, label_suffix=label_suffix, empty_permitted=empty_permitted, **kwargs)
        contexts = sorted(get_models_with_decorator('is_query_context', INSTALLED_APPS))
        self.fields['context'].choices = [(x, bw_titleize(x)) for x in contexts]

    def delete(self, commit=True):
        if self.request.c_user.role.id == self.parent_instance.id:
            raise EntityNotEditableException("You cannot edit filters for your own role.")
        with transaction.atomic():
            role = self.parent_instance
            for _filter in self.child_instances:
                role.filters.remove(_filter)
            role.save(commit)
            return filter

    def save(self, commit=True):
        if self.request.c_user.role.id == self.parent_instance.id:
            raise EntityNotEditableException("You cannot edit filters for your own role.")
        with transaction.atomic():
            _filter = super().save(commit)
            role = self.parent_instance
            for x in filter(lambda a: a.context == _filter.context, role.filters.all()):
                role.filters.remove(x)
            role.filters.add(_filter)
            role.save(commit)
            return _filter

    class Meta:
        model = QueryFilter
        fields = ['context']
