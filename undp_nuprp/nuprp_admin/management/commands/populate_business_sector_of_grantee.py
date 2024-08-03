from django.core.management import BaseCommand

from undp_nuprp.approvals.models import SEFBusinessGrantee


class Command(BaseCommand):
    def handle(self, *args, **options):
        grantees = []
        for grantee in SEFBusinessGrantee.objects.filter(type_of_business__isnull=False
                                                         ).select_related('type_of_business'):
            grantee.business_sector = grantee.type_of_business.parent
            grantees.append(grantee)

        SEFBusinessGrantee.objects.bulk_update(grantees, batch_size=200)
