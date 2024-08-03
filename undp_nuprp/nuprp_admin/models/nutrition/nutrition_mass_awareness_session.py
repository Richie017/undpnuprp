from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Mahbub, Shuvro'


class NutritionMassAwarenessSession(OrganizationDomainEntity):
    number_of_events_held_last_month_by_type_of_issue = models.IntegerField(null=True, blank=True)
    issue_name = models.CharField(null=True, blank=True, max_length=128)
    approximate_number_of_male_participants = models.IntegerField(null=True, blank=True)
    approximate_number_of_female_participants = models.IntegerField(null=True, blank=True)

    class Meta:
        app_label = 'nuprp_admin'

    @classmethod
    def table_columns(cls):
        return [
            "number_of_events_held_last_month_by_type_of_issue:Number of events held last month by type of issue/theme",
            "issue_name:Name of Events/Issue name",
            "approximate_number_of_male_participants:Number of male participants in the events",
            "approximate_number_of_female_participants:Number of female participants in the events"
        ]
