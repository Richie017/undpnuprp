from collections import OrderedDict
from tokenize import group

from django.db import models
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.utility import is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.models import SEFGrantee


@decorate(is_object_context,
          route(route='grantees-by-wpi', group='Local Economy Livelihood and Financial Inclusion',
                module=ModuleEnum.Analysis,
                display_name='Grantees by Ward Prioritization Index', group_order=3, item_order=26))

class GranteesByWPI(OrganizationDomainEntity):

    class Meta:
        app_label = 'approvals'

    city = models.CharField(null=True, blank=True, max_length=20)
    ward = models.CharField(null=True, blank=True, max_length=20)
    ward_poverty_index = models.CharField(null=True, blank=True, max_length=20)
    total_population = models.CharField(null=True, blank=True, max_length=20)
    total_pg_registration = models.CharField(null=True, blank=True, max_length=20)
    average_mpi_ward_wise = models.CharField(null=True, blank=True, max_length=20)
    sef_grantees = models.CharField(null=True, blank=True, max_length=20)
    nutrition_grantees = models.CharField(null=True, blank=True, max_length=20)
    sif_grantees = models.CharField(null=True, blank=True, max_length=20)
    crmif_grantees = models.CharField(null=True, blank=True, max_length=20)
    total_grantee = models.CharField(null=True, blank=True, max_length=20)
    total_family_member_benefited = models.CharField(null=True, blank=True, max_length=20)


    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.AdvancedExport, ViewActionEnum.Delete]

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details, ViewActionEnum.Edit]

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Export"
    