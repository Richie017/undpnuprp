"""
    Created by tareq on 8/8/19
"""
from datetime import datetime

from django.core.management import BaseCommand

from undp_nuprp.approvals.models import EligibleBusinessGrantee, EligibleApprenticeshipGrantee, EligibleEducationGrantee
from undp_nuprp.nuprp_admin.models import CDC, PrimaryGroup, PrimaryGroupMember

__author__ = "Tareq"


class Command(BaseCommand):
    def handle(self, *args, **options):
        target_cdcs = CDC.objects.filter(assigned_code__in=['19026009', '19026010', '19026011'])

        cdc_list = []
        pg_list = []
        member_list = []

        cdc_count = 0
        pg_count = 0
        member_count = 0
        for cdc in target_cdcs:
            print("--------------------------------------------\nHandling cdc: {}".format(cdc.name))
            cdc_code = cdc.assigned_code
            cdc_code = cdc_code.replace("190260", "190250")
            cdc.assigned_code = cdc_code

            cdc_list.append(cdc)

            cdc_count += 1

            target_pgs = PrimaryGroup.objects.filter(parent_id=cdc.pk)
            for pg in target_pgs:
                print(">>>>>>>>>>>>>>>>> Handling PG: {}".format(pg.name))
                pg_code = pg.assigned_code
                pg_code = pg_code.replace("190260", "190250")
                pg.assigned_code = pg_code
                pg_list.append(pg)

                pg_count += 1

                target_members = PrimaryGroupMember.objects.filter(assigned_to_id=pg.pk)
                for member in target_members:
                    print("Handling member: {}".format(member.name))
                    member_code = member.assigned_code
                    member_code = member_code.replace("190260", "190250")
                    member.assigned_code = member_code
                    member_list.append(member)

                    member_count += 1

                    update_time = datetime.now().timestamp() * 1000
                    EligibleBusinessGrantee.objects.filter(pg_member_id=member.pk).update(last_updated=update_time)
                    EligibleEducationGrantee.objects.filter(pg_member_id=member.pk).update(last_updated=update_time)
                    EligibleApprenticeshipGrantee.objects.filter(pg_member_id=member.pk).update(
                        last_updated=update_time)
        CDC.objects.bulk_update(cdc_list, batch_size=300)
        PrimaryGroup.objects.bulk_update(pg_list, batch_size=300)
        PrimaryGroupMember.objects.bulk_update(member_list, batch_size=300)
        print("Updated {} CDCs, {} PGs and {} members".format(cdc_count, pg_count, member_count))
