from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.modules.module import BWModule

__author__ = 'mahmudul'


class RolePermission(OrganizationDomainEntity):
    context = models.CharField(max_length=200)
    display_name = models.CharField(max_length=500, default='')
    app_label = models.CharField(max_length=125, default='')
    group = models.ForeignKey(BWModule, null=True, on_delete=models.SET_NULL)
    group_name = models.CharField(max_length=250, default='')
    route_name = models.CharField(max_length=250, default='')
    item_order = models.IntegerField(default=0)
    is_virtual_model = models.BooleanField(default=False)
    hide = models.BooleanField(default=False)

    @classmethod
    def default_order_by(cls):
        return 'display_name'

    def __str__(self):
        module = BWModule.objects.filter(pk=self.group_id).first()
        if module and module.parent_id:
            return module.render_name + ' -> ' + self.display_name
        return self.group_name + ' -> ' + self.display_name


