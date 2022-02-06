from collections import OrderedDict

from django.core.management.base import BaseCommand

from undp_nuprp.nuprp_admin.models import PrimaryGroupMember, SavingsAndCreditGroup

__author__ = 'Ziaul Haque'


class Command(BaseCommand):
    def handle(self, *args, **options):
        pg_member_queryset = PrimaryGroupMember.objects.values('id', 'assigned_to')

        pg_member_dict = OrderedDict()
        for pg_member in pg_member_queryset:
            pg_member_id = pg_member['id']
            pg_id = pg_member['assigned_to']
            if pg_id not in pg_member_dict.keys():
                pg_member_dict[pg_id] = list()
            pg_member_dict[pg_id].append(pg_member_id)

        _count = 0
        for scg in SavingsAndCreditGroup.objects.all():
            if scg.primary_group_id in pg_member_dict.keys():
                pg_members = pg_member_dict[scg.primary_group_id]
                scg.members.add(*pg_members)
                _count += 1

        print("Total %d SCG updated." % _count)
