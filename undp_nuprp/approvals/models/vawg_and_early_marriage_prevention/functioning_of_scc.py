from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity


class FunctionOfSCC(OrganizationDomainEntity):
    scc_last_hold_its_quarterly_review_meeting = models.DateField(null=True, blank=True)
    number_of_male = models.IntegerField(null=True, default=0)
    number_of_female = models.IntegerField(null=True, default=0)
    number_of_disabled = models.IntegerField(null=True, default=0)
    number_of_disabled_male = models.IntegerField(null=True, default=0)
    number_of_disabled_female = models.IntegerField(null=True, default=0)
    number_of_transsexual = models.IntegerField(null=True, default=0)
    number_of_participants = models.IntegerField(null=True, default=0)
    parts_of_the_scc_plan_included_within_the_cap = models.CharField(null=True, blank=True, max_length=128)
    any_scc_bi_annual_meeting_held_till_date = models.CharField(null=True, blank=True, max_length=3)
    how_many_scc_bi_annual_meeting_held_till_date = models.IntegerField(null=True, default=0)

    class Meta:
        app_label = 'approvals'

    @classmethod
    def table_columns(cls):
        return ('scc_last_hold_its_quarterly_review_meeting',
                'number_of_male', 'number_of_female', 'number_of_disabled', 'number_of_transsexual',
                'number_of_participants',
                'parts_of_the_scc_plan_included_within_the_cap', 'any_scc_bi_annual_meeting_held_till_date')
