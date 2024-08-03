from django.core.management import BaseCommand
from django.db.models import Min

from undp_nuprp.approvals.models import EligibleBusinessGrantee, EligibleApprenticeshipGrantee, EligibleEducationGrantee
from undp_nuprp.nuprp_admin.models import PrimaryGroupMember, DuplcateIdAlert
from undp_nuprp.reports.models import PGMemberInfoCache
from undp_nuprp.survey.models import SurveyResponse, PGMPIIndicator, PGPovertyIndex

__author__ = 'Ziaul Haque'


class Command(BaseCommand):
    def handle(self, *args, **options):
        enumerator_ids = [975, 972]
        pg_ids = ['1101801906', '1101801905', '1101801904', '1101801903', '1101801902', '1101801901']

        survey_responses = SurveyResponse.objects.filter(
            created_by_id__in=enumerator_ids,
            respondent_client__assigned_to__assigned_code__in=pg_ids
        )
        survey_response_ids = survey_responses.values_list('id', flat=True)
        cutoff_time = survey_responses.aggregate(Min('date_created'))['date_created__min']

        primary_group_members = PrimaryGroupMember.objects.filter(surveyresponse__in=survey_responses)

        pg_mpi_indicators = PGMPIIndicator.objects.filter(
            survey_response__in=survey_responses,
            primary_group_member__in=primary_group_members
        )

        pg_poverty_indexes = PGPovertyIndex.objects.filter(primary_group_member__in=primary_group_members)

        pg_member_info_caches = PGMemberInfoCache.objects.filter(to_time__gte=cutoff_time)

        alerts = DuplcateIdAlert.objects.filter(created_by_id__in=enumerator_ids, object_id__in=survey_response_ids)

        eligible_business_grantees = EligibleBusinessGrantee.objects.filter(
            pg_member__primary_group_member__in=primary_group_members
        )

        eligible_apprenticeship_grantees = EligibleApprenticeshipGrantee.objects.filter(
            pg_member__primary_group_member__in=primary_group_members
        )

        eligible_education_grantees = EligibleEducationGrantee.objects.filter(
            pg_member__primary_group_member__in=primary_group_members
        )

        print("Deleting total %d PGMemberInfoCache objects." % pg_member_info_caches.count())
        pg_member_info_caches.delete()

        print("Deleting total %d PGPovertyIndex objects." % pg_poverty_indexes.count())
        pg_poverty_indexes.delete()

        print("Deleting total %d PGMPIIndicator objects." % pg_mpi_indicators.count())
        pg_mpi_indicators.delete()

        print("Deleting total %d PrimaryGroupMember objects." % primary_group_members.count())
        primary_group_members.delete()

        print("Deleting total %d SurveyResponse objects." % survey_responses.count())
        survey_responses.delete()

        print("Deleting total %d DuplcateIdAlert objects." % alerts.count())
        alerts.delete()

        print("Deleting total %d EligibleBusinessGrantee objects." % eligible_business_grantees.count())
        eligible_business_grantees.delete()

        print("Deleting total %d EligibleApprenticeshipGrantee objects." % eligible_apprenticeship_grantees.count())
        eligible_apprenticeship_grantees.delete()

        print("Deleting total %d EligibleEducationGrantee objects." % eligible_education_grantees.count())
        eligible_education_grantees.delete()
