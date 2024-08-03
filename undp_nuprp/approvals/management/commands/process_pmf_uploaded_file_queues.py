from django.core.management import BaseCommand

from undp_nuprp.approvals.models import PMFUploadedFileQueue

__author__ = 'Ziaul Haque'


class Command(BaseCommand):
    def handle(self, *args, **options):
        PMFUploadedFileQueue.process_scheduled_queues()
