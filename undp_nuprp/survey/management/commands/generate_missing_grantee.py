"""
    Created by Shuvro on 22/07/17
"""

from django.core.management.base import BaseCommand

from undp_nuprp.approvals.managers.eligible_grantee_manager import EligibleGranteeManager
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group_member import PrimaryGroupMember
from undp_nuprp.survey.models.response.survey_response import SurveyResponse

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        pgm_ids = PrimaryGroupMember.objects.filter(eligiblebusinessgrantee__isnull=True).values_list('pk', flat=True)
        candidate_responses = SurveyResponse.objects.filter(respondent_client__in=pgm_ids)
        handled = 0
        print('Staring generation')

        for _sr in candidate_responses:
            print('Generating for survey responses: {}'.format(_sr.id))
            mpi_score = EligibleGranteeManager.get_respondent_mpi_score(_sr)
            is_female_headed = EligibleGranteeManager.get_respondent_female_headed_status(_sr)

            try:
                EligibleGranteeManager.handle_eligible_for_business_grant(_sr, mpi_score, is_female_headed)
            except Exception as exp:
                print(str(_sr.pk), exp)

            try:
                EligibleGranteeManager.handle_eligible_for_apprenticeship_grant(_sr, mpi_score, is_female_headed)
            except Exception as exp:
                print(str(_sr.pk), exp)

            try:
                EligibleGranteeManager.handle_eligible_for_drop_out_grant(_sr, mpi_score, is_female_headed)
            except Exception as exp:
                print(str(_sr.pk), exp)

            try:
                EligibleGranteeManager.handle_eligible_for_early_marriage_grant(_sr, mpi_score, is_female_headed)
            except Exception as exp:
                print(str(_sr.pk), exp)

            handled += 1

        print('Grantee generation completed')