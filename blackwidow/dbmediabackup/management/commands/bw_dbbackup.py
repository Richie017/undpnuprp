"""
Command for backup database.
"""
from dbbackup import utils, settings
from dbbackup.db.base import get_connector
from dbbackup.management.commands import dbbackup
from dbbackup.storage import get_storage, StorageError
from django.core.management.base import CommandError

from blackwidow.dbmediabackup.models.backup_task_queue import DBMediaBackupTaskQueue
from blackwidow.dbmediabackup.utils.storage import BWStorage


class Command(dbbackup.Command):
    def handle(self, **options):
        self.verbosity = int(options.get('verbosity'))
        self.quiet = options.get('quiet')
        self.clean = options.get('clean')

        self.servername = options.get('servername')
        self.compress = options.get('compress')
        self.encrypt = options.get('encrypt')

        self.filename = options.get('output_filename')
        self.path = options.get('output_path')
        self.storage = get_storage()

        self.database = options.get('database') or ''
        database_keys = self.database.split(',') or settings.DATABASES

        for database_key in database_keys:
            self.connector = get_connector(database_key)
            database = self.connector.settings
            try:
                filename = self._save_new_backup(database)
                if self.clean:
                    deleted_filename_list = self._cleanup_old_backups(database=database_key)
                    DBMediaBackupTaskQueue.hide_deleted_backup(deleted_backup_list=deleted_filename_list)
                return filename
            except StorageError as err:
                raise CommandError(err)

    def _save_new_backup(self, database):
        if not self.quiet:
            self.logger.info("Backing Up Database: %s", database['NAME'])
        filename = self.connector.generate_filename(self.servername)
        outputfile = self.connector.create_dump()
        if self.compress:
            compressed_file, filename = utils.compress_file(outputfile, filename)
            outputfile = compressed_file
        if self.encrypt:
            encrypted_file, filename = utils.encrypt_file(outputfile, filename)
            outputfile = encrypted_file
        filename = self.filename if self.filename else filename
        if not self.quiet:
            self.logger.info("Backup size: %s", utils.handle_size(outputfile))
        # Store backup
        outputfile.seek(0)
        if self.path is None:
            self.write_to_storage(outputfile, filename)
        else:
            self.write_local_file(outputfile, self.path)
        return filename

    def _cleanup_old_backups(self, database=None, servername=None):
        _storage_instance = BWStorage()
        deleted_filenames = _storage_instance.clean_old_backups(
            encrypted=self.encrypt,
            compressed=self.compress,
            content_type=self.content_type,
            database=database,
            servername=servername)

        return deleted_filenames
