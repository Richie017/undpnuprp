from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Ziaul Haque'


class SEFInstallment(OrganizationDomainEntity):
    installment_id = models.CharField(max_length=255, blank=True, null=True)
    installment_value = models.CharField(max_length=255, blank=True, null=True)
    installment_date = models.DateField(default=None, null=True)
    remarks = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        app_label = 'approvals'

    @classmethod
    def table_columns(cls):
        return (
            "installment_id:Instalment number", "installment_value:Value of instalment",
            "installment_date:Date instalment received by grantee"
        )
