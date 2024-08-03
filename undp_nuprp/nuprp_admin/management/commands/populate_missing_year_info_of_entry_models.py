from datetime import datetime

from django.core.management import BaseCommand

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.approvals.models import VAWGEarlyMarriagePreventionReporting
from undp_nuprp.nuprp_admin.models import CDCAssessment, CommunityActionPlan, CommunityScorecard, \
    CommunityPurchaseCommittee, SocialAuditCommittee

__author__ = "Ziaul Haque"

default_database = BWDatabaseRouter.get_write_database_name()


class Command(BaseCommand):
    def handle(self, *args, **options):
        models = [
            # CDCAssessment,
            # CommunityActionPlan,
            # CommunityScorecard,
            # CommunityPurchaseCommittee,
            # SocialAuditCommittee,
            VAWGEarlyMarriagePreventionReporting,
        ]

        for model in models:
            updatable_items = []
            queryset = model.objects.using(default_database).filter(year="") | model.objects.using(
                default_database).filter(year__isnull=True)

            for item in queryset:
                print("Model: {}, Object: {}".format(model, item))
                try:
                    item.year = datetime.fromtimestamp(item.date_created / 1000).year
                    updatable_items.append(item)
                except Exception as exp:
                    print(exp)
            if len(updatable_items) > 0:
                print("Updating items of {}".format(model))
                model.objects.bulk_update(using=default_database, objs=updatable_items)
                print("Updated...")
