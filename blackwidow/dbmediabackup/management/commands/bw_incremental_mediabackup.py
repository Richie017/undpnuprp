"""
Command for backup media_dirs.
"""
import os

from dbbackup.management.commands import mediabackup
from dbbackup.storage import get_storage, StorageError
from django.conf import settings
from django.core.files.storage import get_storage_class
from django.core.management.base import CommandError
from django.db.models.aggregates import Max

from blackwidow.core.models import FileObject, ErrorLog
from blackwidow.dbmediabackup.models.backup_task_queue import DBMediaBackupTaskQueue

PROJECT_PATH = settings.PROJECT_PATH


class Command(mediabackup.Command):
    def handle(self, *args, **options):
        try:
            self.media_storage = get_storage_class()()
            self.storage = get_storage()
            filename = self.backup_mediafiles()
            return filename

        except StorageError as err:
            raise CommandError(err)

    def backup_mediafiles(self):
        _PROJECT_PATH = PROJECT_PATH.replace(os.sep, '/')
        media_backup_completion_time = DBMediaBackupTaskQueue.objects.aggregate(
            Max('media_backup_completion_time'))['media_backup_completion_time__max']

        media_files = list(FileObject.objects.filter(
            last_updated__gte=media_backup_completion_time
        ).values_list('file', flat=True))
        media_files = filter(bool, media_files)
        media_files = map(lambda x: x.replace(os.sep, '/'), media_files)
        media_files = map(lambda x: x.replace(_PROJECT_PATH, '/'), media_files)
        media_files = map(lambda x: x.replace('//', ''), media_files)
        media_dirs = map(lambda x: x.replace(os.sep, '/'), self._explore_storage())

        unsync_media_files = list(set(media_files) & set(media_dirs))

        for _media_filename in unsync_media_files:
            _media_file = self.media_storage.open(_media_filename)
            try:
                self.write_to_storage(_media_file, _media_filename)
            except Exception as exp:
                ErrorLog.log(exp)
        return ''
