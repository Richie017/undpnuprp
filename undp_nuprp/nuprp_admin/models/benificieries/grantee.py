from collections import OrderedDict

from django.db import models
from django.utils.safestring import mark_safe

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = "Tareq, Shama"


@decorate(is_object_context,
          route(route='grantees', group='Beneficiaries', module=ModuleEnum.Analysis,
                display_name='Grantee', group_order=6, item_order=3, hide=True))
class Grantee(OrganizationDomainEntity):
    is_pg_member = models.BooleanField(default=False)
    referred_pg_member = models.ForeignKey('nuprp_admin.PrimaryGroupMember', null=True, on_delete=models.SET_NULL)
    relation_with_pg_member = models.CharField(max_length=128)
    town = models.ForeignKey('core.Geography', null=True, on_delete=models.SET_NULL)
    gender = models.CharField(max_length=128, blank=True)
    age = models.IntegerField(null=True)
    religion = models.CharField(max_length=128, blank=True)
    ethnicity = models.CharField(max_length=128, blank=True)
    highest_level_of_education = models.CharField(max_length=256, blank=True)
    type_of_grant = models.CharField(max_length=128, blank=True)
    area_of_business = models.CharField(max_length=128, blank=True)
    contact_no = models.CharField(max_length=128, blank=True)
    contract_start_date = models.DateField(null=True)
    contract_end_date = models.DateField(null=True)
    first_installment_date = models.DateField(null=True)

    class Meta:
        app_label = 'nuprp_admin'

    def get_choice_name(self):
        return self.code

    @property
    def render_detail_title(self):
        return mark_safe(str(self.display_name()))

    @classmethod
    def table_columns(cls):
        return ('render_code', 'referred_pg_member:PG Member', 'relation_with_pg_member', 'type_of_grant',
                'contract_start_date', 'contract_end_date')

    @property
    def details_config(self):
        details = OrderedDict()
        details['detail_title'] = self.render_detail_title
        details['code'] = self.code
        details['referred_pg_member'] = self.referred_pg_member
        details['relation_with_pg_member'] = self.relation_with_pg_member
        details['type_of_grant'] = self.type_of_grant
        details['gender'] = self.gender
        details['age'] = self.age
        details['religion'] = self.religion
        details['ethnicity'] = self.ethnicity
        details['highest_level_of_education'] = self.highest_level_of_education
        details['type_of_grant'] = self.type_of_grant
        details['area_of_business'] = self.area_of_business
        details['contact_no'] = self.contact_no
        details['contract_start_date'] = self.contract_start_date
        details['contract_end_date'] = self.contract_end_date
        details['first_installment_date'] = self.first_installment_date
        details['last_updated_by'] = self.last_updated_by
        details['last_updated_on'] = self.render_timestamp(self.last_updated)
        details['created_by'] = self.created_by
        details['created_on'] = self.render_timestamp(self.date_created)
        return details
