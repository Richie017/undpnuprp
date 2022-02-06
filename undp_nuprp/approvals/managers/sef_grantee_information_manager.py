from django.db import transaction

from undp_nuprp.approvals.models import SEFBusinessGrantee, SEFApprenticeshipGrantee, SEFEducationDropoutGrantee, \
    SEFEducationChildMarriageGrantee, EligibleBusinessGrantee, EligibleApprenticeshipGrantee, \
    EligibleEducationDropOutGrantee, EligibleEducationEarlyMarriageGrantee


class SEFGranteeInformationManager(object):
    @classmethod
    def sync_sef_business_grantee_info_from_eligible_business_grantee(cls):
        with transaction.atomic():
            print('Starting business grantee sync...')
            count = 0
            for grantee in SEFBusinessGrantee.objects.all():
                if grantee.age is None or grantee.gender is None or grantee.address is None:
                    eligible = EligibleBusinessGrantee.objects.filter(
                        pg_member__assigned_code=grantee.pg_member_assigned_code)
                    eligible = eligible.filter(grantee_name=grantee.name).first()
                    if eligible:
                        grantee.age = eligible.age
                        grantee.gender = eligible.gender
                        grantee.address = eligible.address
                        grantee.save()
                        count += 1
            print('Total synced:', count)

    @classmethod
    def sync_sef_apprenticeship_grantee_info_from_eligible_apprenticeship_grantee(cls):
        with transaction.atomic():
            print('Starting apprenticeship grantee sync...')
            count = 0
            for grantee in SEFApprenticeshipGrantee.objects.all():
                if grantee.age is None or grantee.gender is None or grantee.address is None:
                    eligible = EligibleApprenticeshipGrantee.objects.filter(
                        pg_member__assigned_code=grantee.pg_member_assigned_code)
                    eligible = eligible.filter(grantee_name=grantee.name).first()
                    if eligible:
                        grantee.age = eligible.age
                        grantee.gender = eligible.gender
                        grantee.address = eligible.address
                        grantee.save()
                        count += 1
            print('Total synced: ', count)

    @classmethod
    def sync_sef_dropout_grantee_info_from_eligible_dropout_grantee(cls):
        with transaction.atomic():
            print('Starting dropout grantee sync...')
            count = 0
            for grantee in SEFEducationDropoutGrantee.objects.all():
                if grantee.age is None or grantee.gender is None or grantee.address is None:
                    eligible = EligibleEducationDropOutGrantee.objects.filter(
                        pg_member__assigned_code=grantee.pg_member_assigned_code)
                    eligible = eligible.filter(grantee_name=grantee.name).first()
                    if eligible:
                        grantee.age = eligible.age
                        grantee.gender = eligible.gender
                        grantee.address = eligible.address
                        grantee.save()
                        count += 1
            print('Total synced: ', count)

    @classmethod
    def sync_sef_early_marriage_grantee_info_from_eligible_early_marriage_grantee(cls):
        with transaction.atomic():
            print('Starting child/early marriage grantee sync...')
            count = 0
            for grantee in SEFEducationChildMarriageGrantee.objects.all():
                if grantee.age is None or grantee.gender is None or grantee.address is None:
                    eligible = EligibleEducationEarlyMarriageGrantee.objects.filter(
                        pg_member__assigned_code=grantee.pg_member_assigned_code)
                    eligible = eligible.filter(grantee_name=grantee.name).first()
                    if eligible:
                        grantee.age = eligible.age
                        grantee.gender = eligible.gender
                        grantee.address = eligible.address
                        grantee.save()
                        count += 1
            print('Total synced: ', count)
