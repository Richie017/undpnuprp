import os
from multiprocessing.synchronize import Lock
from threading import Thread

from django.apps import apps
from django.db import transaction

from blackwidow.engine.file_handlers.file_path_handler import FilePathHandler

get_model = apps.get_model
from django.shortcuts import redirect

from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.generics.importer.generic_importer import GenericImporter
from blackwidow.core.models.config.importer_lock import ImporterLock
from blackwidow.core.models.queue.import_queue import ImportFileQueue
from blackwidow.core.models.queue.queue import FileQueueEnum
from blackwidow.core.signals.signals import import_completed
from django.conf import settings

S3_STATIC_ENABLED = settings.S3_STATIC_ENABLED

__author__ = 'Mahmud'


class GenericImportRunnerView(GenericListView):
    @classmethod
    def run_import(cls, queue, lock_object, request):
        user = request.c_user
        try:
            model = get_model(queue.model.split('.')[0], queue.model.split('.')[1])
            importer_config = model.importer_config(organization=user.organization)
            file_name = FilePathHandler.get_absolute_path(file=queue.file.file)
            temporary_files = []
            if S3_STATIC_ENABLED:
                temporary_files.append(file_name)
            imported_items = GenericImporter.import_from_excel(
                filename=file_name, model=model, user=queue.created_by,
                importer_config=importer_config, request=request
            )
            import_completed.send(
                model, items=imported_items,
                user=queue.created_by,
                organization=user.organization
            )
            model.post_processing_import_completed(
                items=imported_items,
                user=queue.created_by,
                organization=user.organization
            )
            queue.status = FileQueueEnum.COMPLETED

            # after successfully import, remove local file
            for temp_file in temporary_files:
                try:
                    os.remove(temp_file)
                except:
                    pass
        except Exception as exp:
            ErrorLog.log(exp, organization=user.organization)
            queue.status = FileQueueEnum.ERROR
        with transaction.atomic():
            lock_object.is_locked = False
            lock_object.save()
            queue.save()

    def start_background_worker(self, request=None, **kwargs):
        queue = ImportFileQueue.objects.filter(
            status=FileQueueEnum.SCHEDULED,
            organization=request.c_user.organization
        )
        for q in queue:
            lock = Lock(ctx=None)
            lock.acquire(True)
            lock_object, result = ImporterLock.objects.get_or_create(
                model=q.model,
                organization=request.c_user.organization
            )
            if ~lock_object.is_locked:
                with transaction.atomic():
                    lock_object.is_locked = True
                    lock_object.save()
                    q.status = FileQueueEnum.PROCESSING
                    q.save()
                    process = Thread(target=GenericImportRunnerView.run_import, args=(q, lock_object, request))
                    process.start()
            lock.release()

    def get(self, request, *args, **kwargs):
        self.start_background_worker(request=request, **kwargs)
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(GenericImportRunnerView, self).get_context_data(**kwargs)
        context['import'] = True
        return context
