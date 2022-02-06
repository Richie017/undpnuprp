from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from undp_nuprp.approvals.models.infrastructures.base.completed_contract import CompletedContract
from undp_nuprp.approvals.models.infrastructures.base.sanitary_intervention import SanitaryIntervention
from undp_nuprp.approvals.models.infrastructures.base.water_intervention import WaterIntervention


class Intervention(OrganizationDomainEntity):
    type_of_intervention = models.CharField(max_length=256, blank=True, null=True)
    intervention_id = models.CharField(max_length=128, blank=True, null=True)
    number_of_facilities = models.IntegerField(null=True)
    length = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    budget = models.IntegerField(null=True)
    matching_fund = models.IntegerField(null=True, blank=True)
    expected_start_date = models.DateField(default=None, null=True)
    expected_end_date = models.DateField(default=None, null=True)
    number_of_fully_completed_intervention = models.IntegerField(null=True)
    number_of_ongoing_interventions = models.IntegerField(null=True)
    percentage_of_ongoing_interventions = models.IntegerField(null=True)
    date_of_progress_reporting = models.DateField(null=True)
    number_of_total_pg_member_beneficiary = models.IntegerField(null=True)
    number_of_male_pg_member_beneficiary = models.IntegerField(null=True)
    number_of_female_pg_member_beneficiary = models.IntegerField(null=True)
    number_of_total_non_pg_member_beneficiary = models.IntegerField(null=True)
    number_of_male_non_pg_member_beneficiary = models.IntegerField(null=True)
    number_of_female_non_pg_member_beneficiary = models.IntegerField(null=True)
    number_of_family_people_with_disabilities_male = models.IntegerField(null=True)
    number_of_family_people_with_disabilities_female = models.IntegerField(null=True)
    number_of_family_people_with_disabilities_total = models.IntegerField(null=True)
    repair_or_new_project = models.CharField(max_length=10, null=True, blank=True)
    water_interventions = models.ManyToManyField(WaterIntervention)
    sanitary_interventions = models.ManyToManyField(SanitaryIntervention)
    completed_contract = models.ForeignKey(CompletedContract, null=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'approvals'

    @classmethod
    def table_columns(cls):
        return (
            'type_of_intervention', 'intervention_id:Intervention ID', 'number_of_facilities:No. of Facilities',
            'length', 'budget', 'expected_start_date', 'expected_end_date',
            'number_of_fully_completed_intervention:Number of fully completed Facilities',
            'number_of_ongoing_interventions:Number of ongoing Facilities',
            'percentage_of_ongoing_interventions:Percentage of ongoing Facilities', 'date_of_progress_reporting',
            'number_of_total_pg_member_beneficiary:No. of PG members benefiting',
            'number_of_male_pg_member_beneficiary: No. of male PG members benefiting',
            'number_of_female_pg_member_beneficiary: No. of female PG members benefiting',
            'number_of_total_non_pg_member_beneficiary:No. of Non-PG members benefiting',
            'number_of_male_non_pg_member_beneficiary:No. of male Non-PG members benefiting',
            'number_of_female_non_pg_member_beneficiary:No. of female Non-PG members benefiting',
            'number_of_family_people_with_disabilities_total:No. of people with disabilities benefiting',
            'number_of_family_people_with_disabilities_male:No. of male with disabilities benefiting',
            'number_of_family_people_with_disabilities_female:No. of female with disabilities benefiting',
            'repair_or_new_project')

    @classmethod
    def export_file_columns(cls):
        """
        this method is used to get the list of columns to be exported
        :return: a list of column properties
        """
        return list(cls.table_columns())

    @classmethod
    def sortable_columns(cls):
        return []
