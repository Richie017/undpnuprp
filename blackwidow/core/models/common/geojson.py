from django.contrib.gis.db.models import MultiPolygonField
from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Kaikobud, Ziaul Haque'


class GeoJson(OrganizationDomainEntity):
    geography = models.ForeignKey('core.Geography', null=True, on_delete=models.SET_NULL)
    multi_polygon_actual = MultiPolygonField()
    multi_polygon_medium = MultiPolygonField(null=True)
    multi_polygon_low = MultiPolygonField(null=True)

    class Meta:
        app_label = 'core'
