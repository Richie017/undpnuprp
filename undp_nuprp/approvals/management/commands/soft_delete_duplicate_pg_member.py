from django.core.management import BaseCommand

from blackwidow.core.models import ConsoleUser
from undp_nuprp.approvals.models import EligibleBusinessGrantee, EligibleApprenticeshipGrantee, \
    EligibleEducationEarlyMarriageGrantee, EligibleEducationDropOutGrantee
from undp_nuprp.nuprp_admin.models import PrimaryGroupMember

__author__ = 'Ziaul Haque'


class Command(BaseCommand):
    def handle(self, *args, **options):
        queryset = PrimaryGroupMember.objects.filter(surveyresponse__isnull=True)
        all_queryset = PrimaryGroupMember.objects.all()
        superuser = ConsoleUser.objects.get(pk=1)

        member_ids = []
        for pgm in queryset:
            if pgm.assigned_code not in member_ids:
                member_ids.append(pgm.assigned_code)
            print(pgm.assigned_code)

        member_dict = {}
        for pgm in all_queryset:
            if pgm.assigned_code not in member_dict.keys():
                member_dict[pgm.assigned_code] = 0
            member_dict[pgm.assigned_code] += 1
            print(pgm.assigned_code)

        final_member_ids = []
        for code in member_ids:
            count = member_dict.get(code, 0)
            if count > 1:
                final_member_ids.append(code)
            print(code)

        final_queryset = queryset.filter(assigned_code__in=final_member_ids)

        excludable_member_ids = []
        excludable_member_ids += list(EligibleBusinessGrantee.objects.filter(
            pg_member__in=final_queryset
        ).values_list('pg_member_id', flat=True))

        excludable_member_ids += list(EligibleApprenticeshipGrantee.objects.filter(
            pg_member__in=final_queryset
        ).values_list('pg_member_id', flat=True))

        excludable_member_ids += list(EligibleEducationEarlyMarriageGrantee.objects.filter(
            pg_member__in=final_queryset
        ).values_list('pg_member_id', flat=True))

        excludable_member_ids += list(EligibleEducationDropOutGrantee.objects.filter(
            pg_member__in=final_queryset
        ).values_list('pg_member_id', flat=True))

        final_queryset = final_queryset.exclude(pk__in=excludable_member_ids)
        print("Total- {0}".format(final_queryset.count()))

        for pgm in final_queryset:
            print(pgm)
            pgm.soft_delete(force_delete=True, user=superuser)
