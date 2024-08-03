from django.core.management import BaseCommand

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.approvals.models import SEFBusinessGrantee, SEFEducationChildMarriageGrantee, \
    SEFEducationDropoutGrantee, SEFApprenticeshipGrantee, SEFNutritionGrantee

__author__ = 'Ziaul Haque'


class Command(BaseCommand):
    def handle(self, *args, **options):
        models = [
            SEFBusinessGrantee, SEFEducationChildMarriageGrantee,
            SEFEducationDropoutGrantee, SEFApprenticeshipGrantee,
            SEFNutritionGrantee
        ]
        write_db = BWDatabaseRouter.get_write_database_name()

        for MODEL in models:
            queryset1 = MODEL.objects.using(write_db).filter(ward="")
            queryset2 = MODEL.objects.using(write_db).filter(ward__isnull=True)
            queryset = queryset1 | queryset2
            total_items = queryset.count()
            processed_items = 0
            updatable_entries = []
            for item in queryset:
                assigned_code = item.pg_member_assigned_code
                processed_items += 1
                if assigned_code:
                    item.ward = assigned_code[3:5] if len(assigned_code) > 4 else ""
                    updatable_entries.append(item)

                if len(updatable_entries) % 500 == 0:
                    print("updating {0}/{1} items of {2}".format(processed_items, total_items, MODEL.__name__))
                    MODEL.objects.bulk_update(objs=updatable_entries, using=write_db)
                    updatable_entries = []
            print("updating {0}/{1} items of {2}".format(processed_items, total_items, MODEL.__name__))
            MODEL.objects.bulk_update(objs=updatable_entries, using=write_db)
