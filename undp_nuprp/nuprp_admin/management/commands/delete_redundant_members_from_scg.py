from django.core.management import BaseCommand

from blackwidow.core.models import ErrorLog
from undp_nuprp.nuprp_admin.models import SavingsAndCreditGroup


class Command(BaseCommand):
    pg_member_id_list = ['110220060904', '110220060903', '110220060906']
    scg_id = 15875

    def handle(self, *args, **options):
        print("---Started---")
        try:
            scg = SavingsAndCreditGroup.objects.get(pk=self.scg_id)
            scg.members.remove(*scg.members.filter(assigned_code__in=self.pg_member_id_list))
        except Exception as e:
            ErrorLog.log(exp=e)
            print("Error occurred! Check log.")
        print("---Done!---")
