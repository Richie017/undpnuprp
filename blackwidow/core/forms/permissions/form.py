from django import forms
from django.db import transaction
from django.forms.utils import ErrorList

from blackwidow.core.mixins.formmixin.master_slave_form_mixin import GenericMasterSlaveFormMixin
from blackwidow.core.models.permissions.rolepermission import RolePermission
from blackwidow.core.models.roles.role import Role
from blackwidow.engine.constants.access_permissions import *
from blackwidow.engine.decorators.utility import get_models_with_decorator
from blackwidow.engine.exceptions.exceptions import EntityNotEditableException
from blackwidow.engine.extensions import bw_titleize
from config.apps import INSTALLED_APPS

__author__ = 'mahmudul'


class PermissionForm(GenericMasterSlaveFormMixin):
    context = forms.ChoiceField(label='Select context', widget=forms.Select(attrs={'class': 'select2'}), required=False,
                                initial=1)
    access = forms.ChoiceField(label='Select access', widget=forms.Select(attrs={'class': 'select2'}), required=False,
                               initial=4)
    visibility = forms.ChoiceField(label='Visibility Modifier', widget=forms.Select(attrs={'class': 'select2'}),
                                   required=False, initial=0)

    parent_model = Role

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, **kwargs):
        super(PermissionForm, self).__init__(data=data, files=files, auto_id=auto_id, prefix=prefix, initial=initial,
                                             error_class=error_class, label_suffix=label_suffix,
                                             empty_permitted=empty_permitted, **kwargs)
        contexts = sorted(get_models_with_decorator('is_object_context', INSTALLED_APPS))
        self.fields['context'].choices = [(x, bw_titleize(x)) for x in contexts]
        self.fields['access'].choices = sorted([(BW_ACCESS_NO_ACCESS['value'], BW_ACCESS_NO_ACCESS['name']),
                                                (BW_ACCESS_READ_ONLY['value'], BW_ACCESS_READ_ONLY['name']),
                                                (BW_ACCESS_MODIFY_ONLY['value'], BW_ACCESS_MODIFY_ONLY['name']),
                                                (BW_ACCESS_CREATE_MODIFY['value'], BW_ACCESS_CREATE_MODIFY['name']),
                                                (BW_ACCESS_CREATE_MODIFY_DELETE['value'],
                                                 BW_ACCESS_CREATE_MODIFY_DELETE['name'])], reverse=True)

        self.fields['visibility'].choices = sorted([(BW_VISIBILITY_SELF['value'], BW_VISIBILITY_SELF['name']),
                                                    (BW_VISIBILITY_ALL['value'], BW_VISIBILITY_ALL['name'])],
                                                   reverse=True)

    def delete(self, commit=True):
        if self.request.c_user.role.id == self.parent_instance.id:
            raise EntityNotEditableException("You cannot edit permissions for your own role.")
        with transaction.atomic():
            role = self.parent_instance
            for permission in self.child_instances:
                role.permissions.remove(permission)
            role.save(commit)

    def save(self, commit=True):
        if self.request.c_user.role.id == self.parent_instance.id:
            raise EntityNotEditableException("You cannot edit permissions for your own role.")
        with transaction.atomic():
            permission = super().save(commit)
            role = self.parent_instance
            for x in filter(lambda a: a.context == permission.context, role.permissions.all()):
                role.permissions.remove(x)
            role.permissions.add(permission)
            role.save(commit)
            return permission

    class Meta:
        model = RolePermission
        fields = ['context', 'access', 'visibility']
