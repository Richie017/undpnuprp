from datetime import datetime
from django.db import models
from django.utils.safestring import mark_safe

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc import CDC
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc_cluster import CDCCluster

__author__ = 'Shuvro'


@decorate(is_object_context,
          route(route='community-mobilization-reporting', group='Social Mobilization and Community Capacity Building',
                module=ModuleEnum.Analysis, display_name='Community Mobilization Reporting ', group_order=2,
                item_order=2)
          )
class CommunityMobilizationReporting(OrganizationDomainEntity):
    city = models.ForeignKey('core.Geography', null=True)
    cdc_cluster = models.ForeignKey(CDCCluster, null=True, on_delete=models.SET_NULL, related_name='+')
    cdc = models.ForeignKey(CDC, null=True, on_delete=models.SET_NULL, related_name='+')
    year = models.IntegerField(default=1970, null=True)
    month = models.IntegerField(default=1, null=True)
    type_of_meeting = models.CharField(null=True, blank=True, max_length=128)
    ward_number = models.CharField(null=True, blank=True, max_length=128)
    settlement_name = models.CharField(null=True, blank=True, max_length=512)
    num_of_male_participants = models.IntegerField(null=True, blank=True)
    num_of_female_participants = models.IntegerField(null=True, blank=True)
    meeting_date = models.DateField(null=True, blank=True)
    meeting_venue = models.CharField(null=True, blank=True, max_length=256)
    key_discussion_points = models.CharField(null=True, blank=True, max_length=1024)
    key_decision_points = models.CharField(null=True, blank=True, max_length=1024)

    @property
    def detail_title(self):
        return mark_safe(str(self.display_name()))

    @property
    def render_city(self):
        return self.city.name if self.city else 'N/A'

    @property
    def render_month(self):
        return datetime.now().replace(month=self.month).strftime("%B")

    @property
    def render_ward_number(self):
        return self.render_city + '-' + self.ward_number if self.ward_number else 'N/A'

    @property
    def render_CDC_name(self):
        return self.cdc.name if self.cdc else 'N/A'

    @property
    def render_CDC_Cluster(self):
        return self.cdc_cluster.name if self.cdc_cluster else 'N/A'

    @classmethod
    def details_view_fields(cls):
        return 'detail_title', 'render_city>Basic information', 'render_ward_number>Basic information', \
               'render_CDC_name:CDC name>Basic information', 'render_CDC_Cluster:CDC Cluster>Basic information', \
               'render_month>Basic information', 'year>Basic information', 'type_of_meeting>Meeting Details', \
               'settlement_name>Meeting Details', 'num_of_male_participants>Meeting Details', \
               'num_of_female_participants>Meeting Details', 'meeting_date:Date of meeting>Meeting Details', \
               'meeting_venue:Venue of meeting>Meeting Details', 'key_discussion_points>Meeting Details', \
               'key_decision_points>Meeting Details', 'created_by>Meeting Details', 'date_created>Meeting Details', \
               'last_updated_by>Meeting Details', 'last_updated>Meeting Details'

    @classmethod
    def table_columns(cls):
        return ['code', 'render_city', 'ward_number', 'render_CDC_Cluster', 'render_CDC_name', 'render_month',
                'year', 'created_by', 'date_created', 'last_updated_by', 'last_updated:Last Updated On']

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.AdvancedExport]

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details, ViewActionEnum.Edit, ViewActionEnum.AdvancedExport]

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Export"
        elif button == ViewActionEnum.AdvancedImport:
            return "Import"
