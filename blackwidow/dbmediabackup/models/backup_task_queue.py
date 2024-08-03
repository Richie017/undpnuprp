from collections import OrderedDict
from datetime import datetime
from io import StringIO

from dbbackup.utils import bytes_to_str
from django.conf import settings
from django.core.management import call_command
from django.db import models
from django.utils.safestring import mark_safe

from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.dbmediabackup.models.restore_task_queue import RestoreTaskQueue
from blackwidow.dbmediabackup.utils.downloader import BWDownloader
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.exceptions import BWException
from blackwidow.engine.extensions import Clock
from blackwidow.scheduler.models.task_queue import SchedulerTaskQueue, SchedulerTaskQueueEnum

COMPRESS_CLEANUP_OPTIONS = settings.COMPRESS_CLEANUP_OPTIONS

__author__ = 'Ziaul Haque'


@decorate(is_object_context,
          route(route='db-media-backup', group='Logs', module=ModuleEnum.Settings, display_name='Backup Log'))
class DBMediaBackupTaskQueue(SchedulerTaskQueue):
    db_filename = models.CharField(max_length=256, null=True, default=None)
    media_filename = models.CharField(max_length=256, null=True, default=None)
    db_size = models.BigIntegerField(editable=False, null=True, blank=True)
    media_size = models.BigIntegerField(editable=False, null=True, blank=True)
    media_backup_completion_time = models.BigIntegerField(editable=False, default=0)
    start_time = models.BigIntegerField(editable=False, null=True, blank=True)
    completion_time = models.BigIntegerField(editable=False, null=True, blank=True)
    extra_info = models.CharField(max_length=8000, null=True, default=None)

    class Meta:
        app_label = 'dbmediabackup'

    @property
    def render_performed_on(self):
        return self.render_timestamp(self.date_created)

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
    def db_download_url(self):
        if self.db_filename:
            _storage_client = BWDownloader.storage_client()
            if _storage_client.exists(self.db_filename):
                try:
                    _url = _storage_client.url(self.db_filename)
                    return mark_safe("<a class='inline-link' href='" + _url + "' >" + self.db_filename + "</a>")
                except:
                    return "N/A"
        return "N/A"

    @property
    def media_download_url(self):
        if self.media_filename:
            _storage_client = BWDownloader.storage_client()
            if _storage_client.exists(self.db_filename):
                try:
                    _url = _storage_client.url(self.media_filename)
                    return mark_safe("<a class='inline-link' href='" + _url + "' >" + self.media_filename + "</a>")
                except:
                    return "N/A"
        return "N/A"

    @property
    def render_db_size(self):
        if self.db_size:
            _size = self.db_size
            return bytes_to_str(_size)
        return "N/A"

    @property
    def render_media_size(self):
        if self.media_size:
            _size = self.media_size
            return bytes_to_str(_size)
        return "N/A"

    @property
    def details_config(self):
        details = OrderedDict()
        details['code'] = self.code
        details['name'] = self.name
        details['status'] = self.render_status
        details['Database Backup Size'] = self.render_db_size
        details['Performed By'] = self.created_by
        details['Performed On'] = self.render_performed_on
        details['backup_started_on'] = self.render_start_time
        details['backup_completed_on'] = self.render_completion_time
        details['Download Database'] = self.db_download_url
        return details

    def details_link_config(self, **kwargs):
        return []

    def mutate_to(self, cls=None):
        self.is_locked = True
        if self.db_filename and self.media_filename:
            RestoreTaskQueue.create_restore_task_queue(self.db_filename, self.media_filename)
        self.save()
        return self

    @property
    def is_downloadable(self):
        if self.db_filename and self.media_filename:
            if self.db_filename != '' and self.media_filename != '':
                storage_client = BWDownloader.storage_client()
                return storage_client.exists(self.db_filename) and storage_client.exists(self.media_filename)
            return False
        return False

    @classmethod
    def create_backup_task_queue(cls):
        obj = cls()
        obj.name = datetime.now().__str__()
        obj.save()

    @classmethod
    def perform_db_backup(cls, backup_filename=''):
        try:
            output_stream = StringIO()
            call_command('bw_dbbackup', stdout=output_stream, **COMPRESS_CLEANUP_OPTIONS)
            backup_filename = output_stream.getvalue()[:output_stream.getvalue().find('\n')]
        except Exception as exp:
            ErrorLog.log(exp)
        return backup_filename

    @classmethod
    def perform_media_backup(cls, backup_filename=''):
        try:
            output_stream = StringIO()
            call_command('bw_mediabackup', stdout=output_stream, **COMPRESS_CLEANUP_OPTIONS)
            backup_filename = output_stream.getvalue()[:output_stream.getvalue().find('\n')]
        except Exception as exp:
            ErrorLog.log(exp)
        return backup_filename

    @classmethod
    def perform_incremental_media_backup(cls, backup_filename=''):
        try:
            output_stream = StringIO()
            call_command('bw_incremental_mediabackup', stdout=output_stream)
            return True
        except Exception as exp:
            ErrorLog.log(exp)
            return False

    @classmethod
    def generate_backup(cls):
        backup_tasks = cls.objects.filter(is_deleted=False)
        backup_scheduled_tasks = backup_tasks.filter(
            status=SchedulerTaskQueueEnum.SCHEDULED.value
        ).order_by('date_created')
        backup_processing_tasks = backup_tasks.filter(status=SchedulerTaskQueueEnum.PROCESSING.value)
        restore_processing_tasks = RestoreTaskQueue.objects.filter(
            is_deleted=False,
            status=SchedulerTaskQueueEnum.PROCESSING.value
        )

        if not backup_processing_tasks.exists() and not restore_processing_tasks.exists():
            if backup_scheduled_tasks.exists():
                task = backup_scheduled_tasks.first()
                task.status = SchedulerTaskQueueEnum.PROCESSING.value
                task.save()
                task.start_time = Clock.timestamp()
                try:
                    db_backup_filename = cls.perform_db_backup()
                    _media_backup_completion_time = Clock.timestamp()
                    incremental_media_backup = cls.perform_incremental_media_backup()
                    if incremental_media_backup:
                        task.media_backup_completion_time = _media_backup_completion_time
                        task.save()
                    storage_client = BWDownloader.storage_client()
                    if storage_client.exists(db_backup_filename) and incremental_media_backup:
                        task.db_size = storage_client.size(db_backup_filename)
                        task.db_filename = db_backup_filename
                        task.status = SchedulerTaskQueueEnum.COMPLETED.value
                    else:
                        task.status = SchedulerTaskQueueEnum.ERROR.value
                except Exception as exp:
                    task.status = SchedulerTaskQueueEnum.ERROR.value
                    ErrorLog.log(exp)
                task.completion_time = Clock.timestamp()
                task.save()

                return True
            return False
        return False

    @classmethod
    def generate_backup_daily(cls):
        _error_occurred = False
        backup_processing_tasks = cls.objects.filter(
            is_deleted=False, status=SchedulerTaskQueueEnum.PROCESSING.value
        )
        restore_processing_tasks = RestoreTaskQueue.objects.filter(
            is_deleted=False, status=SchedulerTaskQueueEnum.PROCESSING.value
        )
        if not backup_processing_tasks.exists() and not restore_processing_tasks.exists():
            organization = Organization.objects.filter(is_master=True)[0]
            task = cls()
            task.name = datetime.now().__str__()
            task.organization = organization
            task.start_time = Clock.timestamp()
            task.save()
            task.status = SchedulerTaskQueueEnum.PROCESSING.value
            task.save()
            try:
                _media_backup_completion_time = Clock.timestamp()
                incremental_media_backup = cls.perform_incremental_media_backup()
                if incremental_media_backup:
                    task.media_backup_completion_time = _media_backup_completion_time
                    task.status = SchedulerTaskQueueEnum.COMPLETED.value
                else:
                    task.status = SchedulerTaskQueueEnum.ERROR.value
                    _error_occurred = True
            except Exception as exp:
                task.status = SchedulerTaskQueueEnum.ERROR.value
                ErrorLog.log(exp)
                _error_occurred = True
            task.completion_time = Clock.timestamp()
            task.save()

        if _error_occurred:
            raise BWException("An error occurred at the time of performing 'DBMedia Backup' task")

    @classmethod
    def hide_deleted_backup(cls, deleted_backup_list=[]):
        for _item in deleted_backup_list:
            try:
                obj = cls.all_objects.filter(db_filename=_item).first()
                obj.is_deleted = True
                obj.save()
            except Exception as exp:
                pass
