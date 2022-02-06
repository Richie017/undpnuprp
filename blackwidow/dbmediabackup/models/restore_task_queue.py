from datetime import datetime

from django.apps import apps
from django.core.management import call_command
from django.db import models
from django.db.models.aggregates import *

from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.models.system.max_sequence import MaxSequence
from blackwidow.dbmediabackup.utils.downloader import BWDownloader
from blackwidow.dbmediabackup.utils.serialize import BWModelSerializer
from blackwidow.scheduler.models.task_queue import SchedulerTaskQueue, SchedulerTaskQueueEnum

__author__ = 'Ziaul Haque'


class RestoreTaskQueue(SchedulerTaskQueue):
    db_filename = models.CharField(max_length=256, null=True, default=None)
    media_filename = models.CharField(max_length=256, null=True, default=None)
    start_time = models.BigIntegerField(editable=False, null=True, blank=True)
    completion_time = models.BigIntegerField(editable=False, null=True, blank=True)
    extra_info = models.CharField(max_length=8000, null=True, default=None)

    class Meta:
        app_label = 'dbmediabackup'

    @classmethod
    def prefix(cls):
        return 'RTQ'

    @property
    def render_start_time(self):
        if self.start_time:
            return self.render_timestamp(self.start_time)
        return '----'

    @property
    def render_completion_time(self):
        if self.completion_time:
            return self.render_timestamp(self.completion_time)
        return '----'

    @property
    def details_config(self):
        return super().details_config

    def details_link_config(self, **kwargs):
        return [

        ]

    @classmethod
    def create_restore_task_queue(cls, db_filename, media_filename):
        obj = cls()
        obj.name = datetime.now().__str__()
        obj.db_filename = db_filename
        obj.media_filename = media_filename
        obj.save()

    @classmethod
    def perform_db_restore(cls, filename):
        temp_file_path = BWDownloader.download_file(filename)
        call_command('bw_dbrestore', uncompress=True, input_path=temp_file_path, interactive=False)
        BWDownloader.delete_file(temp_file_path)

    @classmethod
    def perform_media_restore(cls, filename):
        temp_file_path = BWDownloader.download_file(filename)
        call_command('bw_mediarestore', uncompress=True, input_path=temp_file_path, interactive=False)
        BWDownloader.delete_file(temp_file_path)

    @classmethod
    def update_max_sequence(cls):
        from blackwidow.dbmediabackup.models.backup_task_queue import DBMediaBackupTaskQueue
        max_value = DBMediaBackupTaskQueue.all_objects.aggregate(Max('id'))['id__max']
        max_seqs = MaxSequence.objects.filter(context=DBMediaBackupTaskQueue.__name__)
        if max_seqs.exists():
            max_seq = max_seqs[0]
            max_seq.value = max_value + 1
            max_seq.save()

    @classmethod
    def generate_restore(cls):
        from blackwidow.dbmediabackup.models.backup_task_queue import DBMediaBackupTaskQueue
        backup_processing_tasks = DBMediaBackupTaskQueue.objects.filter(
            is_deleted=False,
            status=SchedulerTaskQueueEnum.PROCESSING.value
        )
        restore_processing_tasks = RestoreTaskQueue.objects.filter(
            is_deleted=False,
            status=SchedulerTaskQueueEnum.PROCESSING.value
        )

        if not backup_processing_tasks.exists() and not restore_processing_tasks.exists():
            restore_scheduled_tasks = RestoreTaskQueue.objects.filter(
                is_deleted=False,
                status=SchedulerTaskQueueEnum.SCHEDULED.value
            ).order_by('-date_created')
            if restore_scheduled_tasks.exists():
                task = restore_scheduled_tasks.first()
                try:
                    task.status = SchedulerTaskQueueEnum.PROCESSING.value
                    task.save()
                    _dbfilename = task.db_filename
                    _mediafilename = task.media_filename
                    storage_client = BWDownloader.storage_client()
                    if storage_client.exists(_dbfilename) and storage_client.exists(_mediafilename):
                        cls.perform_db_restore(filename=_dbfilename)
                        cls.perform_media_restore(filename=_mediafilename)

                        # update json to task queue model data
                        model_list = [v for k, v in apps.all_models['dbmediabackup'].items()]
                        for _model in model_list:
                            BWModelSerializer.deserialize_json(_model)

                        # update task queue max sequence
                        cls.update_max_sequence()
                        DBMediaBackupTaskQueue.all_objects.all().update(status=SchedulerTaskQueueEnum.COMPLETED.value)
                        RestoreTaskQueue.all_objects.all().update(status=SchedulerTaskQueueEnum.COMPLETED.value)
                except Exception as exp:
                    task.status = SchedulerTaskQueueEnum.ERROR.value
                    task.save()
                    ErrorLog.log(exp)
                return True
            return False
        return False
