from django.core.management import BaseCommand
from django.db.models import Min

from undp_nuprp.nuprp_admin.models import Enumerator, PrimaryGroupMember, DuplcateIdAlert
from undp_nuprp.reports.models import PGMemberInfoCache
from undp_nuprp.survey.models import SurveyResponse, PGMPIIndicator, PGPovertyIndex

__author__ = 'Ziaul Haque'


class Command(BaseCommand):
    def handle(self, *args, **options):
        # enumerator_ids = [984, 987, 988, 989]
        enumerator_ids = [1171]  # enumerator login: test.khulna
        enumerators = Enumerator.objects.filter(pk__in=enumerator_ids)

        survey_responses = SurveyResponse.objects.filter(created_by_id__in=enumerator_ids)
        cutoff_time = survey_responses.aggregate(Min('date_created'))['date_created__min']

        primary_group_members = PrimaryGroupMember.objects.filter(surveyresponse__in=survey_responses)

        pg_mpi_indicators = PGMPIIndicator.objects.filter(
            survey_response__in=survey_responses,
            primary_group_member__in=primary_group_members
        )

        pg_poverty_indexes = PGPovertyIndex.objects.filter(primary_group_member__in=primary_group_members)

        alerts = DuplcateIdAlert.objects.filter(created_by_id__in=enumerators)

        if cutoff_time:
            pg_member_info_caches = PGMemberInfoCache.objects.filter(to_time__gte=cutoff_time)

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

        print("Deleting total %d Enumerator objects." % enumerators.count())
        enumerators.delete()

