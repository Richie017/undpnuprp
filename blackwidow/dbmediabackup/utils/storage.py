from dbbackup import utils
from dbbackup.storage import Storage
from django.conf import settings

CLEANUP_KEEP = settings.DBBACKUP_CLEANUP_KEEP
CLEANUP_KEEP_MEDIA = settings.DBBACKUP_CLEANUP_KEEP_MEDIA

__author__ = "Ziaul Haque"


class BWStorage(Storage):
    def __init__(self, storage_path=None, **options):
        super(BWStorage, self).__init__(storage_path, **options)

    def __str__(self):
        return super(BWStorage, self).__str__()

    def delete_file(self, filepath):
        super(BWStorage, self).delete_file(filepath)

    def list_directory(self, path=''):
        return super(BWStorage, self).list_directory(path)

    def write_file(self, filehandle, filename):
        super(BWStorage, self).write_file(filehandle, filename)

    def read_file(self, filepath):
        return super(BWStorage, self).read_file(filepath)

    def list_backups(self, encrypted=None, compressed=None, content_type=None, database=None, servername=None):
        return super(BWStorage, self).list_backups(encrypted, compressed, content_type, database, servername)

    def get_latest_backup(self, encrypted=None, compressed=None, content_type=None, database=None, servername=None):
        return super(BWStorage, self).get_latest_backup(encrypted, compressed, content_type, database, servername)

    def get_older_backup(self, encrypted=None, compressed=None, content_type=None, database=None, servername=None):
        return super(BWStorage, self).get_older_backup(encrypted, compressed, content_type, database, servername)

    def clean_old_backups(self, encrypted=None, compressed=None, content_type=None,
                          database=None, servername=None, keep_number=None):
        if keep_number is None:
            keep_number = CLEANUP_KEEP if content_type == 'db' else CLEANUP_KEEP_MEDIA
        files = self.list_backups(
            encrypted=encrypted, compressed=compressed, content_type=content_type,
            database=database, servername=servername
        )
        files = sorted(files, key=utils.filename_to_date, reverse=True)
        files_to_delete = [fi for i, fi in enumerate(files) if i >= keep_number]
        for filename in files_to_delete:
            self.delete_file(filename)
        return files_to_delete
