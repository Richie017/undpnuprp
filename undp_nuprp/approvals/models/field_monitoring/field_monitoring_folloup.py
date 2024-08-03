from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity


class FieldMonitoringFollowup(OrganizationDomainEntity):
    key_observation = models.TextField(blank=True)
    key_actions = models.TextField(blank=True)
    person_responsible_for_key_action = models.TextField(blank=True)

    @classmethod
    def table_columns(cls):
        return ['code', 'key_observation', 'key_actions', 'person_responsible_for_key_action',
                'created_by', 'created_at', 'last_updated']
