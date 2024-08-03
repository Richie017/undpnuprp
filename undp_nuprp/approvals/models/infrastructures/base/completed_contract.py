from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Shuvro'


class CompletedContract(OrganizationDomainEntity):
    completed_as_expected_date = models.CharField(max_length=10, null=True, blank=True)
    number_of_days_overrun = models.IntegerField(null=True, blank=True)
    number_of_people_employed = models.IntegerField(null=True, blank=True)
    total_number_of_person_days = models.IntegerField(null=True, blank=True)
    within_budget = models.CharField(max_length=10, null=True, blank=True)
    amount_of_budget_overrun = models.IntegerField(null=True, blank=True)
    amount_deposited_to_om_fund = models.IntegerField(null=True, blank=True)
    variation_order = models.CharField(max_length=3, null=True, blank=True)
    what_kind_of_changes = models.TextField(blank=True)
    project_completion_report = models.TextField(blank=True)
    project_handover = models.TextField(blank=True)
    post_survey_date = models.DateField(default=None, null=True)
    om_Fund_established_date = models.DateField(default=None, null=True)

    @property
    def render_intervention_ID(self):
        return self.intervention_set.first().intervention_id

    class Meta:
        app_label = 'approvals'

    @classmethod
    def table_columns(cls):
        return (
            'render_intervention_ID', 'completed_as_expected_date:Completed as per expected date',
            'number_of_days_overrun', 'number_of_people_employed', 'total_number_of_person_days', 'within_budget',
            'amount_of_budget_overrun', 'amount_deposited_to_om_fund:Amount deposited to O&M Fund',
            'post_survey_date', 'project_completion_report', 'project_handover', 'om_Fund_established_date',
            'variation_order', 'what_kind_of_changes:What kind of changes?')

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
