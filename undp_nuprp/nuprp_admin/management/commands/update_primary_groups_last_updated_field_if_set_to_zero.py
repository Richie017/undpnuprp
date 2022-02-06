from django.core.management.base import BaseCommand
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group import PrimaryGroup

__author__ = 'Asif Sanjary, Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        _pg_queryset = PrimaryGroup.objects.filter(last_updated=0)

        print("Total {} of Primary Groups having Last Updated field set to 0 (1970) ".format(_pg_queryset.count()))

        _primary_groups = _pg_queryset.all()
        _updated_primary_groups_list = []

        for _each_primary_group in _primary_groups:
            _each_primary_group.last_updated = _each_primary_group.date_created
            _updated_primary_groups_list.append(_each_primary_group)

        if len(_updated_primary_groups_list) > 0:
            PrimaryGroup.objects.bulk_update(_updated_primary_groups_list, batch_size=500)
            print("Successfully replaced the value of \"Last Updated\" field with the value of \"Date Created\" field.")
        else:
            print("Nothing to update")
