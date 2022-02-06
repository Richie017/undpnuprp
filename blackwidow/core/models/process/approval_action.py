from django.db import models

from blackwidow.core.models.common.choice_options import ApprovalStatus
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Sohel'

class ApprovalAction(OrganizationDomainEntity):
    model_name = models.CharField(max_length=100,blank=True,null=True,default='')
    status = models.IntegerField()   ###ApprovalStatus.Approved.value
    remarks = models.TextField(blank=True)
    object_id = models.BigIntegerField(default=0)
    level = models.BigIntegerField(default=0)

    @property
    def render_remarks(self):
        return self.remarks if self.remarks else "N/A"

    @property
    def render_status(self):
        if self.status == ApprovalStatus.Approved.value:
            return "Approved"
        elif self.status == ApprovalStatus.Rejected.value:
            return "Rejected"
        elif self.status == ApprovalStatus.StepBack.value:
            return "Step Back"
        elif self.status == ApprovalStatus.Restore.value:
            return "Restore"
        return "N/A"

    @classmethod
    def table_columns(cls):
        return "code", "render_status", "render_remarks", "created_by:Action Taken By", "date_created"
