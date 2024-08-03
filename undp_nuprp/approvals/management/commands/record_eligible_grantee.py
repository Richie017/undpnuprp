"""
Created by tareq on 2/22/18
"""
from django.core.management import BaseCommand

from undp_nuprp.approvals.managers.eligible_grantee_manager import EligibleGranteeManager

__author__ = 'Tareq'


class Command(BaseCommand):
    def handle(self, *args, **options):
        EligibleGranteeManager.generate()
