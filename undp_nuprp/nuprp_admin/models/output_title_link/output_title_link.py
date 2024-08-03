from collections import OrderedDict
from django.utils.safestring import mark_safe

from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.nuprp_admin.enums.capacity_building_output_enum import CapacityBuildingOutputEnum


__author__ = "Ahsan"

class OutputTitleLink(models.Model):
    title = models.CharField(max_length=255, blank=True)
    output = models.CharField(max_length=255, blank=True)
   

    class Meta:
        app_label = 'nuprp_admin'
        
    
    