"""
    Created by tareq on 5/27/19
"""
from django.core.management import BaseCommand

from undp_nuprp.reports.managers.third_party.third_party_api_manager import ThirdPartyAPIManager

__author__ = "Tareq"


class Command(BaseCommand):
    def handle(self, *args, **options):
        ThirdPartyAPIManager.prepare_third_party_api_data()
