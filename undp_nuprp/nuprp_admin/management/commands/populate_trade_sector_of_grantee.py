from django.core.management import BaseCommand

from undp_nuprp.approvals.models import SEFApprenticeshipGrantee


class Command(BaseCommand):
    def handle(self, *args, **options):
        grantees = []
        for grantee in SEFApprenticeshipGrantee.objects.filter(trade_type__isnull=False
                                                               ).select_related('trade_type'):
            grantee.trade_sector = grantee.trade_type.parent
            grantees.append(grantee)

        SEFApprenticeshipGrantee.objects.bulk_update(grantees, batch_size=200)
