from datetime import datetime

from django.core.management import BaseCommand

from blackwidow.core.models import ErrorLog
from undp_nuprp.approvals.models import SEFGrantDisbursement, SEFBusinessGrantee, SEFApprenticeshipGrantee, \
    SEFEducationDropoutGrantee, SEFEducationChildMarriageGrantee, SEFNutritionGrantee
from undp_nuprp.nuprp_admin.models import PrimaryGroup, PrimaryGroupMember


class Command(BaseCommand):
    pg_dict = {
        '3900501711': '3900501813',
        '3900501712': '3900501814'
    }

    def handle(self, *args, **options):
        print('---Starting Execution---')
        # This command doesn't take care of SCG group members. So, this can't be followed.
        try:
            members = []
            for pair in self.pg_dict:
                pg = PrimaryGroup.objects.filter(assigned_code=self.pg_dict[pair]).first()
                
                member_queryset = PrimaryGroupMember.objects.filter(assigned_to__assigned_code=pair)
                member_count = member_queryset.count()
                processed = 0

                for member in member_queryset:
                    processed += 1
                    print("Processing {}/{}".format(processed, member_count))
                    current_time = datetime.now().timestamp() * 1000
                    prev_code = member.assigned_code
                    new_code = self.pg_dict[pair] + prev_code[10:]
                    member.assigned_to_id = pg.id
                    member.assigned_code = new_code
                    member.last_updated = current_time
                    members.append(member)

                    SEFGrantDisbursement.objects.filter(pg_member_assigned_code=prev_code
                                                        ).update(pg_member_assigned_code=new_code, last_updated=current_time)

                    SEFBusinessGrantee.objects.filter(pg_member_assigned_code=prev_code
                                                      ).update(pg_member_assigned_code=new_code, last_updated=current_time)

                    SEFApprenticeshipGrantee.objects.filter(pg_member_assigned_code=prev_code
                                                            ).update(pg_member_assigned_code=new_code, last_updated=current_time)

                    SEFEducationDropoutGrantee.objects.filter(pg_member_assigned_code=prev_code
                                                              ).update(pg_member_assigned_code=new_code, last_updated=current_time)

                    SEFEducationChildMarriageGrantee.objects.filter(pg_member_assigned_code=prev_code
                                                                    ).update(pg_member_assigned_code=new_code, last_updated=current_time)

                    SEFNutritionGrantee.objects.filter(pg_member_assigned_code=prev_code
                                                       ).update(pg_member_assigned_code=new_code, last_updated=current_time)

            PrimaryGroupMember.objects.bulk_update(members, batch_size=200)
        except Exception as e:
            ErrorLog.log(exp=e)
            print('Exception occurred!')
        print('---Ending Execution---')
