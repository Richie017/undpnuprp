from django.forms.utils import ErrorList

from blackwidow.core.mixins.formmixin.master_slave_form_mixin import GenericMasterSlaveFormMixin
from blackwidow.core.models.permissions.rolepermission_assignment import RolePermissionAssignment
from blackwidow.core.models.roles.role import Role


__author__ = 'mahmudul'


class PermissionAssignmentForm(GenericMasterSlaveFormMixin):

    parent_model = Role

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, **kwargs):
        super().__init__(data=data, files=files, auto_id=auto_id, prefix=prefix, initial=initial, error_class=error_class, label_suffix=label_suffix, empty_permitted=empty_permitted,**kwargs)

    class Meta:
        model = RolePermissionAssignment
        fields = ['access', 'visibility']
