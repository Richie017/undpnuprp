from decimal import Decimal

from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Ziaul Haque'


class InstallmentPayment(OrganizationDomainEntity):
    monthly_installment_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("000.00"),
                                                     null=True, blank=True)
    number_of_due_installments = models.IntegerField(blank=True, null=True)
    total_due_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("000.00"),
                                           null=True, blank=True)
    number_of_paid_installments = models.IntegerField(blank=True, null=True)
    total_repayment_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("000.00"),
                                                 null=True, blank=True)
    number_of_overdue_installments = models.IntegerField(blank=True, null=True)
    overdue_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("000.00"),
                                         null=True, blank=True)
    total_outstanding_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("000.00"),
                                                   null=True, blank=True)

    class Meta:
        app_label = 'nuprp_admin'

    @classmethod
    def table_columns(cls):
        return [
            "monthly_installment_amount:Monthly Installment Amount (in BDT)",
            "number_of_due_installments:Number of Installments Due",
            "total_due_amount:Total Amount Due (in BDT)",
            "number_of_paid_installments:Number of Installment Paid",
            "total_repayment_amount:Total Repayment Amount (in BDT)",
            "number_of_overdue_installments:Number of Installment Overdue",
            "overdue_amount:Overdue Amount (in BDT)",
            "total_outstanding_amount:Total Outstanding Amount (in BDT)",
        ]
