"""
    Created by tareq on 11/4/19
"""
import os

from django.apps import apps
from django.core.management import BaseCommand
from django.db import transaction

from blackwidow.core.generics.importer.generic_importer import GenericImporter
from blackwidow.core.models import ConsoleUser, ImportFileQueue, FileQueueEnum, ErrorLog
from blackwidow.core.signals.signals import import_completed

__author__ = "Tareq"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('param_list', nargs='*', type=str, default='')

    @classmethod
    def run_import(cls, queue):
        user = queue.created_by
        try:
            print("Running import for ", str(queue.model))
            model = apps.get_model(queue.model.split('.')[0], queue.model.split('.')[1])
            importer_config = model.importer_config(organization=user.organization)
            print(importer_config.columns.values('column'))
            print("Loading file ", str(os.path.abspath(queue.file.file.path)))
            imported_items = GenericImporter.import_from_excel(filename=os.path.abspath(queue.file.file.path),
                                                               model=model, user=queue.created_by,
                                                               importer_config=importer_config, )
            print("import items formatted. Found {} records".format(len(imported_items)))
            import_completed.send(model, items=imported_items, user=queue.created_by, organization=user.organization)
            print("Now processing...")
            model.post_processing_import_completed(items=imported_items, user=queue.created_by,
                                                   organization=user.organization)
            print("processing completed.")
            queue.status = FileQueueEnum.COMPLETED
        except Exception as exp:
            ErrorLog.log(exp, organization=user.organization)
            queue.status = FileQueueEnum.ERROR
        with transaction.atomic():
            queue.save()

    def handle(self, *args, **options):
        queue_id = int(options['param_list'][0])

        queue = ImportFileQueue.objects.filter(pk=queue_id)
        for q in queue:
            with transaction.atomic():
                q.status = FileQueueEnum.PROCESSING
                q.save()
                self.run_import(queue=q)
