from django.db import models
from django.utils.safestring import mark_safe

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.permissions.rolepermission import RolePermission
from blackwidow.core.models.roles.role import Role
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'mahmudul'


class RolePermissionAssignment(OrganizationDomainEntity):
    permission = models.ForeignKey(RolePermission, related_name='permission', on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    access = models.IntegerField(default=0)
    visibility = models.IntegerField(default=0)

    class Meta:
        app_label = 'core'
        ordering = ('permission__display_name',)

    @classmethod
    def default_order_by(cls):
        return 'permission'

    @property
    def get_app_label(self):
        return self.permission.app_label if self.permission else None

    @property
    def get_context(self):
        return self.permission.context if self.permission else None

    @property
    def get_inline_manage_buttons(self, **kwargs):
        return [
            dict(
                name='Edit',
                action='edit',
                icon='icon-pencil',
                ajax='1',
                url_name=self.__class__.get_route_name(
                    action=ViewActionEnum.PartialEdit, parent=self.role_set.model.__name__.lower()),
                classes='manage-action load-modal',
                parent=self.role_set.all()[0]
            )
        ]

    def get_simplified_dict(self):
        contexts = self.permission.context.split(',')
        return {
            'access': self.access,
            'visibility': self.visibility,
            'app': contexts[0] if len(contexts) > 1 else '',
            'context': contexts[1] if len(contexts) > 1 else contexts[0]
        }

    @property
    def get_access(self):
        if self.access == 0:
            return 'No Access'
        if self.access == 1:
            return 'View'
        if self.access == 2:
            return 'View/Edit'
        if self.access == 3:
            return 'View/Create/Edit'
        if self.access == 4:
            return 'View/Create/Edit/Delete'
        return self.access

    def render_object_access(self):
        return mark_safe('<select name="' + self.permission.context + '" class="select2 inline-edit-input">' \
                                                                      '<option value="' + str(0) + '" ' + (
                             ' selected="selected"' if self.access == 0 else '') + ' >No Access</option>' \
                                                                                   '<option value="' + str(1) + '" ' + (
                             ' selected="selected"' if self.access == 1 else '') + ' >View</option>' \
                                                                                   '<option value="' + str(2) + '" ' + (
                             ' selected="selected"' if self.access == 2 else '') + ' >View / Edit</option>' \
                                                                                   '<option value="' + str(3) + '" ' + (
                             ' selected="selected"' if self.access == 3 else '') + ' >View / Edit / Create</option>' \
                                                                                   '<option value="' + str(4) + '" ' + (
                             ' selected="selected"' if self.access == 4 else '') + ' >View / Edit / Create / Delete </option>'
                                                                                   '</select>')
        # if not checked:
        #     return mark_safe('<input type="hidden" name="' + self.permission.context + '" value="0" />' +
        #                      '<input class="inline-edit-input" type="checkbox" name="' + self.permission.context + '" value="' + value + '" />')
        # return mark_safe('<input type="hidden" name="' + self.permission.context + '" value="0" />' +
        #                  '<input class="inline-edit-input" type="checkbox" name="' + self.permission.context + '" checked="checked" value="' + value + '" />')

    def render_visibility(self, **kwargs):
        if self.visibility == 0:
            return mark_safe('<span class="label label-warning">All</span>')
        if self.visibility == 1:
            return mark_safe('<span class="label label-success">Self</span>')
        return self.visibility

    def render_object_name(self):
        return self.permission

    @classmethod
    def table_columns(cls):
        return 'render_object_name', 'render_object_access'

