from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Shuvro'


class SIFInstallment(OrganizationDomainEntity):
    installment_number = models.IntegerField(null=True)
    installment_value = models.IntegerField(null=True)
    installment_date = models.DateField(null=True)
    status_of_physical_progress = models.TextField(blank=True)
    status_of_financial_progress = models.IntegerField(null=True)

    class Meta:
        app_label = 'approvals'

    @classmethod
    def table_columns(cls):
        return 'installment_number:Instalment number', 'installment_value:Value of instalment', \
               'installment_date:Date of instalment', \
               'status_of_physical_progress:Status of physical Progress (descriptive)', \
               'status_of_financial_progress:Status of Financial Progress %'

    @classmethod
    def sortable_columns(cls):
        return []
