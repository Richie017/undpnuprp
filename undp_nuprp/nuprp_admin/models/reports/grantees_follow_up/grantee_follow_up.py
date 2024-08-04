"""
Created by tareq on 10/3/17
"""
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from django.db import models

from undp_nuprp.nuprp_admin.models.benificieries.grantee import Grantee

__author__ = 'Tareq'


class GranteeFollowUp(OrganizationDomainEntity):
    grantee = models.ForeignKey(Grantee, on_delete=models.CASCADE)
    date_of_last_installment = models.DateField(null=True)

    class Meta:
        app_label = 'nuprp_admin'
        abstract = True
