from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Shuvro'


class SEFGrantInstalment(OrganizationDomainEntity):
    number = models.CharField(max_length=128, blank=True, null=True)
    value = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=300, blank=True, null=True)
    date = models.DateField(null=True, blank=True)
    remarks = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        app_label = 'approvals'

    @classmethod
    def table_columns(cls):
        return (
            "number:number", "value:Amount (BDT)", "status", "date"
        )
