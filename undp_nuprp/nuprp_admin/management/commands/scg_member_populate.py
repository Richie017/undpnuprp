from django.core.management import BaseCommand

from blackwidow.core.models import ErrorLog
from undp_nuprp.nuprp_admin.models import PrimaryGroup, SavingsAndCreditGroup, PrimaryGroupMember


class Command(BaseCommand):
    pg_id = 206628
    scg_id = 10503

    def handle(self, *args, **options):
        print("---Started---")
        try:
            pg = PrimaryGroup.objects.get(pk=self.pg_id)

            scg = SavingsAndCreditGroup.objects.get(pk=self.scg_id)
            scg.members.add(*PrimaryGroupMember.objects.filter(pk__in=pg.client_set.values_list('pk', flat=True)))
            scg.save()
        except Exception as e:
            ErrorLog.log(exp=e)
            print("Error occurred! Check log.")
        print("---Done!---")
