from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Shuvro'


class SanitaryIntervention(OrganizationDomainEntity):
    type_of_sanitation_before_intervention = models.CharField(max_length=128, null=True, blank=True)
    is_excreta_safely_disposed = models.CharField(max_length=10, null=True, blank=True)
    does_beneficiary_share_sanitation = models.CharField(max_length=10, null=True, blank=True)
    type_of_sanitation_with_intervention = models.CharField(max_length=128, null=True, blank=True)
    will_the_sanitation_be_shared = models.CharField(max_length=10, blank=True, null=True)
    will_excreta_be_safely_disposed = models.CharField(max_length=10, blank=True, null=True)
    if_twin_pit_latrine_are_bottom_of_the_rings_more_than_two_meter = models.CharField(max_length=10, blank=True,
                                                                                        null=True)
    is_the_latrine_at_least_15_meters_from_nearest_water_source = models.CharField(max_length=10, blank=True,
                                                                                   null=True)

    class Meta:
        app_label = 'approvals'

    @property
    def render_intervention_ID(self):
        return self.intervention_set.first().intervention_id

    @classmethod
    def table_columns(cls):
        return (
            "render_intervention_ID",
            "type_of_sanitation_before_intervention:Type of sanitation facility used by intended beneficiaries before "
            "this intervention",
            "is_excreta_safely_disposed:Excreta is safely disposed in situ or transported to a designated place for "
            "safe disposal or treatment",
            "does_beneficiary_share_sanitation:Are the intended beneficiaries currently sharing sanitation facilities",
            "type_of_sanitation_with_intervention:Type of sanitation facility",
            "will_the_sanitation_be_shared:Will the sanitation facility be shared by Hhs",
            "will_excreta_be_safely_disposed:Will excreta be safely disposed of in situ or transported to a designated "
            "place for safe disposal or treatment",
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
