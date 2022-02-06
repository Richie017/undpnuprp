from django.db import models
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Kaikobud'


class UrbanPoorSettlementIndicator(OrganizationDomainEntity):
    settlement = models.ForeignKey('core.Geography', null=True)
    household = models.IntegerField(null=True)
    population = models.IntegerField(null=True)
    settlement_age = models.IntegerField(null=True)
    condition_of_access_road = models.IntegerField(null=True)
    availability_of_drain = models.IntegerField(null=True)
    electricity_coverage = models.IntegerField(null=True)
    solid_waste_collection_service = models.IntegerField(null=True)
    access_to_piped_water_supply = models.IntegerField(null=True)
    availability_of_hygienic_toilet = models.IntegerField(null=True)
    street_lighting = models.IntegerField(null=True)
    attendance_of_children_at_school = models.IntegerField(null=True)
    households_with_employment = models.IntegerField(null=True)
    household_income = models.IntegerField(null=True)
    social_problem = models.IntegerField(null=True)
    land_tenure_security = models.IntegerField(null=True)
    housing_condition = models.IntegerField(null=True)
    risk_of_eviction = models.IntegerField(null=True)
    land_ownership = models.IntegerField(null=True)
    type_of_occupancy = models.IntegerField(null=True)
    total_score = models.IntegerField(null=True)

    class Meta:
        app_label = 'nuprp_admin'
