from django.db import models
from django.utils.safestring import mark_safe

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.modules.module import BWModule
from blackwidow.core.models.permissions.rolepermission import RolePermission
from blackwidow.core.models.roles.role import Role
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'mahmudul'


class ModulePermissionAssignment(OrganizationDomainEntity):
    module = models.ForeignKey(BWModule, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    access = models.IntegerField(default=0)
    visibility = models.IntegerField(default=0)
    landing_model = models.ForeignKey(RolePermission, null=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'core'

    @classmethod
    def default_order_by(cls):
        return 'module'

    @property
    def get_name(self):
        return self.module.name if self.module else None

    @property
    def get_access(self):
        return "Allow" if self.access > 0 else "Deny"

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
        contexts = self.module.name
        return {
            'access': self.access,
            'visibility': self.visibility,
            'app': contexts[0] if len(contexts) > 1 else '',
            'name': contexts[1] if len(contexts) > 1 else contexts[0]
        }

    def render_allow(self):
        return mark_safe('<input type="radio" class="inline-edit-input" name="' + self.module.name + '" value="' +
                         str(1) + '" ' + (' checked="checked"' if self.access == 1 else '') + ' ></input>')

    def render_deny(self):
        return mark_safe('<input type="radio" class="inline-edit-input" name="' + self.module.name + '" value="' +
                         str(0) + '" ' + (' checked="checked"' if self.access == 0 else '') + ' ></input>')

    def render_landing_menu_item(self):
        if self.module.parent is None:
            child_module_names = list(BWModule.objects.filter(parent_id=self.module_id).values_list('name', flat=True))
            child_object_permissions = RolePermission.objects.filter(group_name__in=child_module_names)
            options = ''
            options += '<option value="" > Usual Dashboard </option>'
            for permission in child_object_permissions:
                selected = ''
                if self.landing_model_id == permission.pk:
                    selected = 'selected'
                options += '<option value="' + str(permission.pk) + '" ' + selected + ' >' + permission.group_name + \
                           ' -> ' + permission.display_name + '</option>'
            return mark_safe(
                '<select name="' + self.module.name + '__' + self.role.name +
                '" class="select2 inline-edit-input">' + options +
                '</select>')
        else:
            return 'Not Applicable'

    @classmethod
    def table_columns(cls):
        return 'module', 'render_allow', 'render_deny', 'render_landing_menu_item'
