import uuid
from collections import OrderedDict

from django.db import models

from blackwidow.core.models import ImporterColumnConfig, ImporterConfig, Geography
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators import enable_import
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import Clock

__author__ = 'Kaikobud'


@decorate(is_object_context, route(
    route='cities_towns_with_pro_poor_and_climate_resilient_urban_strategy', group='Interactive Mapping',
    module=ModuleEnum.Analysis,
    display_name='Number of Cities/Towns with Pro Poor and Climate Resilient Urban Strategy Under Implementation',
    group_order=4, item_order=5))
class CitiesTownsWithProPoorClimateResilientUrbanStrategy(OrganizationDomainEntity):
    stage = models.CharField(max_length=32, null=True, blank=True)
    city = models.ForeignKey('core.Geography', null=True)
    name_of_component = models.CharField(max_length=128, null=True, blank=True)
    name_of_assessment = models.CharField(max_length=128, null=True, blank=True)
    status = models.CharField(max_length=32, null=True, blank=True)

    class Meta:
        app_label = 'nuprp_admin'

    @classmethod
    def table_columns(cls):
        return [
            'code', 'stage', 'city', 'name_of_component', 'name_of_assessment', 'status',
            'created_by', 'last_updated'
        ]

    @property
    def details_config(self):
        d = OrderedDict()
        d['Stage'] = self.stage
        d['City'] = self.city
        d['Name of Component'] = self.name_of_component
        d['Name of Assessment'] = self.name_of_assessment
        d['Status'] = self.status

        # audit information
        audit_info = OrderedDict()
        audit_info['last_updated_by'] = self.last_updated_by
        audit_info['last_updated_on'] = self.render_timestamp(self.last_updated)
        audit_info['created_by'] = self.created_by
        audit_info['created_on'] = self.render_timestamp(self.date_created)
        d["Audit Information"] = audit_info

        return d
