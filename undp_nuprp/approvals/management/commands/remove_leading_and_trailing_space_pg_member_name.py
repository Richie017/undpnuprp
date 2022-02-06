from django.core.management import BaseCommand
from django.db import transaction
from django.db.models.query_utils import Q

from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group_member import PrimaryGroupMember

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():

            pgm_queryset = PrimaryGroupMember.objects.filter(Q(name__endswith=' ') | Q(name__startswith=' '))

            print('Total {} member have name contains leading and trailing spaces'.format(pgm_queryset.count()))

            _pg_members = pgm_queryset.all()
            _updated_pg_members_list = []

            for _pgm in _pg_members:
                _pgm.name = _pgm.name.strip()
                _updated_pg_members_list.append(_pgm)

            if len(_updated_pg_members_list) > 0:
                PrimaryGroupMember.objects.bulk_update(_updated_pg_members_list, batch_size=500)
                print('Successfully removed spaces')
            else:
                print('Nothing to update')
