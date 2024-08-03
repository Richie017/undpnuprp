from django.core.management import BaseCommand
from django.db import transaction
from datetime import datetime

from undp_nuprp.nuprp_admin.models import PrimaryGroup, PrimaryGroupMember
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc import CDC
from undp_nuprp.survey.models import SurveyResponse


class Command(BaseCommand):
    change_dict = {'09019084': '09020084',
                   '09019023': '09020023',
                   '09019047': '09020047',
                   '09019048': '09020048',
                   '09020114': '09021114'}
    to_change = list(change_dict.keys())

    def handle(self, *args, **options):
        print('---Starting Execution---')
        with transaction.atomic():
            timestamp = datetime.now().timestamp() * 1000
            for cdc_old_code in self.change_dict.keys():
                cdc = CDC.objects.filter(assigned_code=cdc_old_code).first()
                print("Handling CDC: {}".format(cdc.name,))

                if not cdc:
                    continue

                pgs = PrimaryGroup.objects.filter(parent_id=cdc.pk)
                pg_ids = pgs.values_list('pk', flat=True)

                pg_members = PrimaryGroupMember.objects.filter(assigned_to_id__in=pg_ids)
                member_ids = pg_members.values_list('pk', flat=True)

                survey_responses = SurveyResponse.objects.filter(respondent_client_id__in=member_ids)

                cdc.assigned_code = self.change_dict[cdc_old_code]
                cdc.save()

                print("Updating {} primary groups".format(pgs.count()))
                for pg in pgs:
                    pg.assigned_code = self.change_dict[cdc_old_code] + str(pg.assigned_code)[8:]
                    pg.last_updated = timestamp
                    timestamp += 1
                PrimaryGroup.objects.bulk_update(pgs)
                print("...Updated")

                print("Updating {} primary group members".format(pg_members.count()))
                for pg_member in pg_members:
                    pg_member.assigned_code = self.change_dict[cdc_old_code] + str(pg_member.assigned_code)[8:]
                    pg_member.last_updated = timestamp
                    timestamp += 1
                PrimaryGroupMember.objects.bulk_update(pg_members)
                print("...updated")

                print("Updating {} survey responses".format(survey_responses.count()))
                for sr in survey_responses:
                    sr.last_updated = timestamp
                    timestamp += 1
                SurveyResponse.objects.bulk_update(survey_responses)
                print("...updated")

        print('---Ending Execution---')
