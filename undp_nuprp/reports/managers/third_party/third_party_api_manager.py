"""
    Created by tareq on 5/26/19
"""
from collections import OrderedDict

from django.db.models import Sum, Count

from undp_nuprp.approvals.models import SEFBusinessGrantee, SEFApprenticeshipGrantee, SEFEducationDropoutGrantee, \
    SEFNutritionGrantee, SEFEducationChildMarriageGrantee
from undp_nuprp.reports.models import PGMemberInfoCache, PGMemberCount, DisabledMembersCount, GrantDisbursementCount

__author__ = "Tareq"


class ThirdPartyAPIManager(object):
    @classmethod
    def prepare_third_party_api_data(cls):
        cls.prepare_pg_member_count_data()
        cls.prepare_disabled_member_count_data()
        cls.prepare_grant_disbursement_count_data()

    @classmethod
    def prepare_pg_member_count_data(cls):
        print("Preparing PG member count data.")
        pg_member_cache_queryset = PGMemberInfoCache.objects.all()
        queryset = pg_member_cache_queryset.values(
            'city_id').annotate(count=Sum('pg_count'))

        for q in queryset:
            if not q['city_id']:
                continue
            existing_record = PGMemberCount.objects.filter(city_id=q['city_id']).first()
            if not existing_record:
                existing_record = PGMemberCount(city_id=q['city_id'])
            existing_record.pg_member_count = q['count']
            existing_record.save()
            print(">> {}: PG member count {}".format(existing_record.city.name, existing_record.pg_member_count))

    @classmethod
    def prepare_disabled_member_count_data(cls):
        print("Preparing disabled member count data.")

        pg_member_cache_queryset = PGMemberInfoCache.objects.all()

        queryset = pg_member_cache_queryset.filter(
            disability_counts__label__isnull=False
        ).order_by(
            'city__name', 'disability_counts__label'
        ).values(
            'city_id', 'disability_counts__label'
        ).annotate(
            count=Sum('disability_counts__count')
        )

        for q in queryset:
            if not q['city_id']:
                continue
            existing_record = DisabledMembersCount.objects.filter(
                city_id=q['city_id'],
                disability=q['disability_counts__label']
            ).first()
            if not existing_record:
                existing_record = DisabledMembersCount(
                    city_id=q['city_id'],
                    disability=q['disability_counts__label']
                )
            existing_record.member_count = q['count'] if q['count'] else 0
            existing_record.save()
            print(">> {}: disability '{}' count {}".format(
                existing_record.city.name, existing_record.disability, existing_record.member_count))

    @classmethod
    def prepare_grant_disbursement_count_data(cls):
        print("Preparing grant disbursement count.")

        grantees = OrderedDict()
        grantees[SEFBusinessGrantee] = "Business Grants"
        grantees[SEFApprenticeshipGrantee] = "Apprenticeship Grant"
        grantees[SEFEducationDropoutGrantee] = "Education Grant (Addressing Dropout)"
        grantees[SEFEducationChildMarriageGrantee] = "Education Grant (Early Child Marriage)"
        grantees[SEFNutritionGrantee] = "Nutrition Grant"

        for grantee_class, grant_name in grantees.items():

            grantee_queryset = grantee_class.objects.values(
                'pg_member__assigned_to__parent__address__geography__parent_id'
            ).order_by(
                'pg_member__assigned_to__parent__address__geography__parent__name'
            ).annotate(total=Count('pk'))

            for g in grantee_queryset:
                total_gr = g['total'] if g['total'] else 0
                city_id = g['pg_member__assigned_to__parent__address__geography__parent_id']
                if not city_id:
                    continue

                existing_record = GrantDisbursementCount.objects.filter(
                    city_id=city_id,
                    grant_type=grant_name
                ).first()
                if not existing_record:
                    existing_record = GrantDisbursementCount(
                        city_id=city_id,
                        grant_type=grant_name
                    )
                existing_record.disbursement_count = total_gr
                existing_record.save()
                print(">> {}: '{}' count {}".format(
                    existing_record.city.name, existing_record.grant_type, existing_record.disbursement_count))