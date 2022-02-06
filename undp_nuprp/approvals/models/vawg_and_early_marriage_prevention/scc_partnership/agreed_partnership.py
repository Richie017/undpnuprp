from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Shuvro'


class AgreedPartnership(OrganizationDomainEntity):
    is_agreed_partnership = models.CharField(null=True, blank=True, max_length=128)
    with_which_organisation = models.CharField(null=True, blank=True, max_length=128)
    date_of_agreement = models.DateField(null=True, blank=True)
    duration_of_agreement = models.CharField(null=True, blank=True, max_length=1028)
    partnership_related_to_what = models.CharField(null=True, blank=True, max_length=128)

    class Meta:
        app_label = 'approvals'

    @classmethod
    def table_columns(cls):
        return ['is_agreed_partnership:Status', 'date_of_agreement:Date', 'with_which_organisation:Organization Name',
                'duration_of_agreement:Duration', 'partnership_related_to_what:Partnership Details']
