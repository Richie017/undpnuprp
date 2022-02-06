from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Shuvro'


class ActivitiesOfPartnership(OrganizationDomainEntity):
    conducted_partnership_activities = models.CharField(null=True, blank=True, max_length=128)
    with_which_organisation = models.CharField(null=True, blank=True, max_length=128)
    date_of_activity = models.DateField(null=True, blank=True)
    explanation_of_the_activity = models.CharField(null=True, blank=True, max_length=1028)

    class Meta:
        app_label = 'approvals'

    @classmethod
    def table_columns(cls):
        return ['date_of_activity:Date', 'with_which_organisation:Organization Name',
                'conducted_partnership_activities:Activity Status']
