from multiprocessing.synchronize import Lock
from threading import Thread

from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect

from blackwidow.core.forms.files.importfileobject_form import ImportFileObjectForm
from blackwidow.core.forms.queue.import_queue_form import ImportFileQueueForm
from blackwidow.core.generics.views.create_view import GenericCreateView
from blackwidow.core.generics.views.import_view import GenericImportRunnerView
from blackwidow.core.models.config.importer_lock import ImporterLock
from blackwidow.core.models.queue.import_queue import ImportFileQueue
from blackwidow.core.models.queue.queue import FileQueueEnum
from blackwidow.engine.decorators.utility import get_models_with_decorator
from config.apps import INSTALLED_APPS

__author__ = 'Sohel'


class AdvancedGenericImportView(GenericCreateView):
    form_kwargs = None

    def start_background_worker(self, request=None, **kwargs):
        queues = ImportFileQueue.objects.filter(
            status=FileQueueEnum.SCHEDULED,
            organization=request.c_user.organization
        )
        for q in queues:
            lock = Lock(ctx=None)
            lock.acquire(True)
            lock_object, result = ImporterLock.objects.get_or_create(
                model=q.model, organization=request.c_user.organization
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
        self.form_kwargs = kwargs
        return super(AdvancedGenericImportView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return "/" + self.model.get_model_meta('route', 'route') + "/"

    def post(self, request, *args, **kwargs):
        self.form_kwargs = kwargs
        file_object_form = ImportFileObjectForm(request.POST, request.FILES)
        if file_object_form.is_valid():
            file_object = file_object_form.save()

            import_enabled_models = [(a + "." + x, x) for a, x in
                                     get_models_with_decorator('enable_import', INSTALLED_APPS, app_name=True) if
                                     x == self.model.get_import_model().__name__]

            if import_enabled_models:
                import_file_queue = ImportFileQueueForm({
                    "file": file_object.pk,
                    "model": import_enabled_models[0][0],
                    "status": FileQueueEnum.SCHEDULED
                })
                if import_file_queue.is_valid():
                    import_file_queue.save()
                else:
                    print(import_file_queue.__dict__)

                self.start_background_worker(request=request, **kwargs)
                messages.success(request, self.model.__name__ + ' import is being scheduled and running')
                return redirect(self.get_success_url())
            else:
                messages.error(request, 'This model has not been marked as import enabled.')
                return redirect(self.get_success_url())
        else:
            messages.error(request, 'Invalid Form Data')
            return redirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super(AdvancedGenericImportView, self).get_form_kwargs()
        if self.form_kwargs:
            kwargs.update(self.form_kwargs)
        return kwargs
