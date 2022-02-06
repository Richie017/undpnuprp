from decimal import Decimal

from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'ruddra'


class FinancialInformation(OrganizationDomainEntity):
    dues = models.DecimalField(max_digits=14, decimal_places=3, default=Decimal("000.00"), null=True)
    over_dues = models.DecimalField(max_digits=14, decimal_places=3, default=Decimal("000.00"), null=True)
    last_do_quantity = models.BigIntegerField(null=True, default=None)
    last_delivery_quantity = models.BigIntegerField(null=True, default=None)
    sale_quantity = models.BigIntegerField(null=True, default=0)

    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()

        class Serializer(ss):

            class Meta(ss.Meta):
                model = cls
                fields = ('id', 'tsync_id', 'dues', 'over_dues', 'last_do_quantity',
                          'last_delivery_quantity', 'sale_quantity')

        return Serializer