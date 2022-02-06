from django.core.management import BaseCommand

from undp_nuprp.approvals.models.field_monitoring.field_monitoring_output import FieldMonitoringOutput


class Command(BaseCommand):
    def handle(self, *args, **options):
        outputs = ['Output 1', 'Output 2', 'Output 3', 'Output 4', 'Output 5']

        for o in outputs:
            f = FieldMonitoringOutput(name=o)
            f.save()
