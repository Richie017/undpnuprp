from django.core.urlresolvers import reverse
from django.db import models
from django.utils.safestring import mark_safe

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.roles.role import Role
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'Sohel'


class ApprovalLevel(OrganizationDomainEntity):
    roles = models.ManyToManyField(Role)
    level = models.BigIntegerField(default=0)
    approve_model = models.CharField(max_length=100, default='')
    reject_model = models.CharField(max_length=100, default='')

    @classmethod
    def default_order_by(cls):
        return "level"

    @property
    def render_roles(self):
        make_anchor = lambda x: mark_safe("<a class='inline-link' href='" +
                                          reverse(x.get_route_name(ViewActionEnum.Details),
                                                  kwargs={'pk': x.pk}) + "' >" + x.name + "</a>")
        return mark_safe(','.join([make_anchor(role) for role in self.roles.all()]))

    @classmethod
    def table_columns(cls):
        return "code", "render_roles", "level", "approve_model", "reject_model", "last_updated"
