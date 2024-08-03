from enum import Enum

from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Sohel'


class ApprovalStatusEnum(Enum):
    Created = "as_created"
    Approved = "as_approved"
    Rejected = "as_rejected"
    ReverseRejected = "as_reverse_rejected"


class ProcessBreakdown(OrganizationDomainEntity):
    approval_status = models.CharField(max_length=100,null=True,blank=True)
    process_level = models.CharField(max_length=100,null=True,blank=True)
    description = models.CharField(max_length=2000, null=True, blank=True)
