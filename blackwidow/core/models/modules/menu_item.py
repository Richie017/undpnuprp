from django import forms
from django.db import models

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.modules.module import BWModule
from blackwidow.core.models.permissions.rolepermission import RolePermission

__author__ = 'Mahmud'


class BWMenuItem(OrganizationDomainEntity):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey(BWModule)
    permissions = models.ManyToManyField(RolePermission)

    @classmethod
    def get_form(cls, parent, **kwargs):
        class DynamicForm(parent):

            def __init__(self, **kwargs):
                super(DynamicForm, self).__init__(**kwargs)

                self.fields['parent'] = \
                    GenericModelChoiceField(
                        queryset=BWModule.objects.all().order_by('parent', 'name'),
                        widget=forms.Select(attrs={'class': 'select2'})
                    )

            class Meta:
                model = cls
                fields = ['name', 'parent']

        return DynamicForm

    class Meta:
        unique_together = ('name', 'organization',)
