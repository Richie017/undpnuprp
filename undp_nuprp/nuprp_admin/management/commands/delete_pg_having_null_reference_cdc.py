"""
Created by shuvro on 05/21/2019
"""

from django.core.management import BaseCommand
from django.db import transaction

from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group import PrimaryGroup

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            no_of_pg_to_be_deleted = PrimaryGroup.objects.filter(parent__is_deleted=True).count()
            print('Number of PG having deleted CDC: {}'.format(no_of_pg_to_be_deleted))

            deleted_pg_queryset = PrimaryGroup.objects.filter(parent__is_deleted=True)

            print('Deleting PG with no reference of CDC')
            for _pg in deleted_pg_queryset:
                _pg.soft_delete()

            print('Successfully deleted')
