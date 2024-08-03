"""
Created by shuvro on 27/03/19
"""
from django.core.management.base import BaseCommand

from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group import PrimaryGroup

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Renaming primary group: PG Group 34009000035 to 3400900035')
        PrimaryGroup.objects.filter(assigned_code=34009000035).update(assigned_code=3400900035)
        print('Successfully updated')
