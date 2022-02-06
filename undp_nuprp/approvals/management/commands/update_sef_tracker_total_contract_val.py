"""
    Created by Sayem on 28 January, 2021
    Organization Field Buzz
"""

__author__ = "Sayem"

from django.core.management import BaseCommand
from django.db.models import Case, When, Value, DecimalField, F

from undp_nuprp.approvals.models import SEFTracker


class Command(BaseCommand):
    """
    This command is to re-calculate and update the `total_contract_value` for the existing buggy entries in the
    `SEFTracker` model in both of the `Stage` and `Production` server.
    """
    @staticmethod
    def update_sef_tracker_total_contract_val(*args, **kwargs):
        SEFTracker.objects.exclude(
            contract_value__isnull=True, training_cost__isnull=True, management_fee__isnull=True).annotate(
            final_contract_value=Case(
                When(contract_value__isnull=True, then=Value(0)),
                default=F("contract_value"), output_field=DecimalField()),
            final_training_cost=Case(
                When(training_cost__isnull=True, then=Value(0)),
                default=F("training_cost"), output_field=DecimalField()),
            final_management_fee=Case(
                When(management_fee__isnull=True, then=Value(0)),
                default=F("management_fee"), output_field=DecimalField()),
        ).update(total_contract_value=F("final_contract_value") + F("final_training_cost") + F("final_management_fee"))

    def handle(self, *args, **options):
        self.update_sef_tracker_total_contract_val(*args, **options)
