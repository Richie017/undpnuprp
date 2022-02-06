from django.core.management import BaseCommand

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.approvals.models import *

write_db_alias = BWDatabaseRouter.get_write_database_name()

__author__ = "Ziaul Haque"


class Command(BaseCommand):
    def handle(self, *args, **options):

        models = [
            SEFBusinessGrantDisbursement, SEFApprenticeshipGrantDisbursement,
            SEFEducationChildMarriageGrantDisbursement, SEFEducationDropoutGrantDisbursement
        ]

        for model in models:
            queryset = model.objects.using(
                write_db_alias
            ).filter(grant_disbursement_year__isnull=True)
            updatable_items = []
            for q in queryset:
                try:
                    q.grant_disbursement_year = q.instalments.first().date.year
                    updatable_items.append(q)
                except:
                    pass

                if len(updatable_items) == 500:
                    print("Model: {}, 500 items created.".format(model.__name__))
                    model.objects.bulk_update(objs=updatable_items, using=write_db_alias)
                    updatable_items = []
            if len(updatable_items) > 0:
                print("Model: {}, {} items created.".format(model.__name__, len(updatable_items)))
                model.objects.bulk_update(objs=updatable_items, using=write_db_alias)
