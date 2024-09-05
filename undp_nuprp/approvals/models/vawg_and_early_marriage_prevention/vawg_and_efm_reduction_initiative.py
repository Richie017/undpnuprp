from django.db import models
from django.utils.safestring import mark_safe

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Shuvro'


class VAWGEFMReductionInitiative(OrganizationDomainEntity):
    name_of_issue = models.CharField(null=True, blank=True, max_length=128)
    explanation_regarding_issue = models.CharField(null=True, blank=True, max_length=128)
    attachment = models.ForeignKey('core.FileObject', null=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'approvals'

    @property
    def render_attachment(self):
        _url = self.attachment.get_file_access_path() if self.attachment.file else None
        _title = '<i class="fa fa-download" aria-hidden="true"></i>'
        return 'N/A' if not _url else mark_safe(
            '<a title="Click to download this item" href="' + _url + '" >' + _title + '</a>')

    @classmethod
    def table_columns(cls):
        return 'name_of_issue:Issue Name', 'explanation_regarding_issue:Explanation', 'render_attachment'
