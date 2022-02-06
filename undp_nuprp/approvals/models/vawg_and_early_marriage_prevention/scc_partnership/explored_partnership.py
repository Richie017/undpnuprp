from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Shuvro'


class ExploredPartnership(OrganizationDomainEntity):
    is_partnerships_explored = models.CharField(null=True, blank=True, max_length=128)
    with_which_organisation = models.CharField(null=True, blank=True, max_length=128)
    date_of_partnership = models.DateField(null=True, blank=True)
    partnership_related_to_what = models.CharField(null=True, blank=True, max_length=128)

    class Meta:
        app_label = 'approvals'

    @classmethod
    def table_columns(cls):
        return ['is_agreed_partnership:Status', 'date_of_agreement:Date', 'with_which_organisation:Organization Name',
                'partnership_related_to_what:Partnership Details']
