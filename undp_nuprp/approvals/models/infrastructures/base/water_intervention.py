from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Shuvro'


class WaterIntervention(OrganizationDomainEntity):
    source_of_drinking_before_intervention = models.CharField(max_length=128, null=True, blank=True)
    water_collection_time_from_existing_point = models.CharField(max_length=128, null=True, blank=True)
    type_of_water_intervention = models.CharField(max_length=128, null=True, blank=True)
    water_collection_time_with_this_intervention = models.CharField(max_length=128, null=True, blank=True)
    has_water_quality_been_checked_by_laboratory = models.CharField(max_length=32, null=True, blank=True)
    has_water_quality_been_checked_by_laboratory_for_physical = models.CharField(max_length=32, null=True, blank=True)
    has_water_quality_been_checked_by_laboratory_for_pH = models.CharField(max_length=32, null=True, blank=True)
    has_water_quality_been_checked_by_laboratory_for_turbidity = models.CharField(max_length=32, null=True, blank=True)
    has_water_quality_been_checked_by_laboratory_for_chemical = models.CharField(max_length=32, null=True, blank=True)
    has_water_quality_been_checked_by_laboratory_for_arsenic = models.CharField(max_length=32, null=True, blank=True)
    has_water_quality_been_checked_by_laboratory_for_acc_level = models.CharField(max_length=32, null=True,
                                                                                         blank=True)
    has_water_quality_been_checked_by_laboratory_for_nitrate = models.CharField(max_length=32, null=True, blank=True)
    has_water_quality_been_checked_by_laboratory_for_florid = models.CharField(max_length=32, null=True, blank=True)
    has_water_quality_been_checked_by_laboratory_for_magnesium = models.CharField(max_length=32, null=True, blank=True)
    has_water_quality_been_checked_by_laboratory_dissolved_solid = models.CharField(max_length=32, null=True,
                                                                                              blank=True)
    has_water_quality_been_checked_by_laboratory_microbiological = models.CharField(max_length=32, null=True,
                                                                                        blank=True)
    has_water_quality_been_checked_by_laboratory_fecal_coliform = models.CharField(max_length=32, null=True,
                                                                                       blank=True)

    class Meta:
        app_label = 'approvals'

    @property
    def render_intervention_ID(self):
        return self.intervention_set.first().intervention_id

    @classmethod
    def table_columns(cls):
        return (
            "render_intervention_ID",
            "source_of_drinking_before_intervention:Source of drinking water for intended beneficiaries before "
            "this intervention",
            "water_collection_time_from_existing_point:Estimated average time taken for the intended beneficiaries to "
            "collect water from their existing water point",
            "type_of_water_intervention:Type of water intervention",
            "water_collection_time_with_this_intervention:Estimated average time taken for the intended beneficiaries "
            "to collect water with this intervention"
        )

    @classmethod
    def export_file_columns(cls):
        """
        this method is used to get the list of columns to be exported
        :return: a list of column properties
        """
        return list(cls.table_columns()[1:])

    @classmethod
    def sortable_columns(cls):
        return []
