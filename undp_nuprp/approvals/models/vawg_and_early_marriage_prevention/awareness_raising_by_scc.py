from django.db import models
from django.utils.safestring import mark_safe

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Shuvro'


class AwarenessRaisingBySCC(OrganizationDomainEntity):
    campaign_date = models.DateField(null=True, blank=True)
    activity_name = models.CharField(null=True, blank=True, max_length=128)
    please_specify = models.TextField(blank=True)
    campaign_location_city = models.ForeignKey('core.Geography', null=True, related_name='city', on_delete=models.SET_NULL)  # ward number
    campaign_location_ward = models.ForeignKey('core.Geography', null=True, related_name='ward', on_delete=models.SET_NULL)  # ward number
    number_of_female_attending = models.IntegerField(null=True, default=0)
    number_of_male_attending = models.IntegerField(null=True, default=0)
    number_of_disabled_male_attending = models.IntegerField(null=True, default=0)
    number_of_disabled_female_attending = models.IntegerField(null=True, default=0)
    number_of_transgender_attending = models.IntegerField(null=True, default=0)
    number_of_lgi_member_attending = models.IntegerField(null=True, default=0)
    campaign_key_messages = models.CharField(null=True, blank=True, max_length=2048)
    name_of_usage_method = models.CharField(null=True, blank=True, max_length=128)
    attachment = models.ForeignKey('core.FileObject', null=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'approvals'

    @property
    def render_attachment(self):
        _url = self.attachment.get_file_access_path() if self.attachment else None
        _title = '<i class="fa fa-download" aria-hidden="true"></i>'
        if _url:
            return mark_safe('<a title="Click to download this item" href="' + _url + '" >' + _title + '</a>')
        return "N/A"

    @property
    def render_campaign_location(self):
        return str(self.campaign_location_ward.parent.name + '-' + self.campaign_location_ward.name) \
            if self.campaign_location_ward else 'N/A'

    @property
    def render_campaign_location_ward(self):
        return str(self.campaign_location_ward.name) if self.campaign_location_ward else 'N/A'

    @classmethod
    def table_columns(cls):
        return ['campaign_date:Date', 'activity_name:Explanation', 'please_specify:Specification (if any)',
                'render_campaign_location_ward',
                'number_of_female_attending:Female',
                'number_of_male_attending:Male',
                'number_of_transgender_attending:Transgender',
                'number_of_disabled_male_attending:Disabled male',
                'number_of_disabled_female_attending:Disabled female',
                'number_of_lgi_member_attending:LGI member',
                'campaign_key_messages:Key messages', 'name_of_usage_method:Used method', 'render_attachment']
