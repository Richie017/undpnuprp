from django import forms
from django.db import transaction

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.modules.module import BWModule
from blackwidow.core.models.permissions.modulepermission_assignment import ModulePermissionAssignment
from blackwidow.core.models.permissions.rolepermission import RolePermission
from blackwidow.core.models.permissions.rolepermission_assignment import RolePermissionAssignment
from blackwidow.core.models.roles.role import Role
from blackwidow.engine.constants.access_permissions import BW_ACCESS_READ_ONLY, BW_VISIBILITY_ALL
from blackwidow.engine.decorators.utility import get_models_with_decorator
from config.apps import INSTALLED_APPS

__author__ = 'mahmudul'


class RoleForm(GenericFormMixin):
    name = forms.CharField(max_length=500)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].required = False

    def save(self, commit=True):
        with transaction.atomic():
            instance = super().save(commit)

            if self.is_new_instance:
                permission_models = get_models_with_decorator('is_object_context', INSTALLED_APPS)
                instance.permissions.clear()
                for model in permission_models:
                    perm, result = RolePermission.objects.get_or_create(
                        organization=instance.organization, context=model)
                    if result:
                        perm.save()
                    RolePermissionAssignment.objects.create(permission=perm, role=instance,
                                                            organization=instance.organization,
                                                            access=BW_ACCESS_READ_ONLY['value'],
                                                            visibility=BW_VISIBILITY_ALL['value'])

                modules = BWModule.objects.all()
                for m in modules:
                    if instance.modules.filter(name=m.name).exists():
                        continue
                    mass = ModulePermissionAssignment()
                    mass.organization = instance.organization
                    mass.module = m
                    mass.role = instance
                    mass.access = 1
                    mass.visibility = 0
                    mass.save()

            return instance

    class Meta(GenericFormMixin.Meta):
        model = Role
        fields = ['name', 'parent', 'get_alert', 'landing_url']
        widgets = {
            'parent': forms.SelectMultiple(attrs={'class': 'select2'}),
        }
        labels = {
            'parent': 'Parent Role/Reports To'
        }
