from collections import OrderedDict

from django.core.management import BaseCommand
from django.db.models import Value, Count
from django.db.models.functions import Concat

from blackwidow.core.models import Geography, ContactAddress, GeoJson, ConsoleUser
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.approvals.models import LowCostHousingUnit, WordPrioritizationIndicator, MobilizedPrimaryGroupMember, \
    AwarenessRaisingBySCC, SEFBusinessGrantee, SEFApprenticeshipGrantee, SEFEducationChildMarriageGrantee, \
    SEFEducationDropoutGrantee, SEFNutritionGrantee, FieldMonitoringReport, SEFTracker
from undp_nuprp.nuprp_admin.models import LandTenureSecurity, Meeting, CommunityMobilizationReporting, CDCAssessment, \
    CommunityActionPlan, CommunityPurchaseCommittee, CommunityScorecard, SocialAuditCommittee
from undp_nuprp.reports.models import QuestionResponseCache, PGMemberInfoCache, SEFGranteesInfoCache

__author__ = 'Ziaul Haque'

write_db = BWDatabaseRouter.get_write_database_name()


class Command(BaseCommand):

    @classmethod
    def execute_part_one(cls, *args, **kwargs):
        ward_names = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        print(Geography.objects.using(write_db).filter(
            level__name="Ward", name__in=ward_names
        ).update(name=Concat(Value("0"), 'name')))

    @classmethod
    def execute_part_two(cls, *args, **kwargs):
        queryset = Geography.objects.using(write_db).filter(
            level__name="Ward"
        ).values(
            'parent', 'parent__name', 'name'
        ).annotate(Count('pk')).filter(pk__count__gt=1).order_by('parent', 'name')

        duplicate_ward_dict = OrderedDict()
        for item in queryset:
            key = (item['parent'], item['name'])
            duplicate_ward_dict[key] = list(Geography.objects.using(write_db).filter(
                parent=item['parent'], name=item['name']
            ).values_list('pk', flat=True).order_by('pk'))

        models = [
            (LowCostHousingUnit, 'ward'),
            (WordPrioritizationIndicator, 'Ward'),
            (MobilizedPrimaryGroupMember, 'ward'),
            (LandTenureSecurity, 'ward'),
            (QuestionResponseCache, 'ward'),
            (PGMemberInfoCache, 'ward'),
            (ContactAddress, 'geography'),
            (GeoJson, 'geography'),
            (Geography, 'parent'),
            (AwarenessRaisingBySCC, 'campaign_location_ward'),
        ]

        deletable_wards = []
        for key, ward_list in duplicate_ward_dict.items():
            original_ward = ward_list[0]
            duplicate_wards = ward_list[1:]
            for model, field in models:
                queryset = model.all_objects.using(write_db).filter(
                    **{field + '__in': duplicate_wards}
                )
                print(key, model.__name__, queryset.count())
                queryset.update(**{field: original_ward})
                print("updated...")
                deletable_wards += duplicate_wards

        superuser = ConsoleUser.objects.using(write_db).first()
        print("soft deleting duplicate wards...")
        deletable_queryset = Geography.objects.using(write_db).filter(pk__in=set(deletable_wards))
        for item in deletable_queryset:
            item.soft_delete(force_delete=True, user=superuser)
        print("soft deletion of duplicate wards have been completed.")

    @classmethod
    def execute_part_three(cls, *args, **kwargs):
        models = [
            (SEFBusinessGrantee, 'ward'),
            (SEFApprenticeshipGrantee, 'ward'),
            (SEFEducationChildMarriageGrantee, 'ward'),
            (SEFEducationDropoutGrantee, 'ward'),
            (SEFNutritionGrantee, 'ward'),

            (FieldMonitoringReport, 'ward'),

            (SEFTracker, 'ward'),
            # ConsoleUser.assigned_code
            # InfrastructureUnit.address
            # InfrastructureUnit.assigned_code
            (Meeting, 'ward_number'),

            (SEFGranteesInfoCache, 'ward'),
            (CommunityMobilizationReporting, 'ward_number'),
            (CDCAssessment, 'ward_no'),
            (CommunityActionPlan, 'ward_no'),
            (CommunityPurchaseCommittee, 'ward_no'),
            (CommunityScorecard, 'ward_no'),
            (SocialAuditCommittee, 'ward_no'),
        ]

        ward_names = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

        for model, field in models:
            queryset = model.all_objects.using(write_db).filter(**{field + '__in': ward_names})

            print(model.__name__, queryset.count())
            queryset.update(**{field: Concat(Value("0"), field)})
            print("updated...")

    def handle(self, *args, **options):
        self.execute_part_one(*args, **options)
        self.execute_part_two(*args, **options)
        self.execute_part_three(*args, **options)
