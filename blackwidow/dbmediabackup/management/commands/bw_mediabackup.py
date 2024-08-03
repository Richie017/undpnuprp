"""
Command for backup media_dirs.
"""
import os

from dbbackup import utils
from dbbackup.management.commands import mediabackup
from dbbackup.storage import get_storage, StorageError
from django.core.files.storage import get_storage_class
from django.core.management.base import CommandError

from settings import DBBACKUP_MEDIA_PATH


class Command(mediabackup.Command):
    def handle(self, *args, **options):
        self.clean = options.get('clean', False)
        self.encrypt = options.get('encrypt', False)
        self.compress = options.get('compress', False)
        self.servername = options.get('servername')
        self.filename = options.get('output_filename')
        self.path = options.get('output_path')
        try:
            self.media_storage = get_storage_class()()
            self.storage = get_storage()
            filename = self.backup_mediafiles()
            if self.clean:
                self._cleanup_old_backups(servername=self.servername)
            return filename

        except StorageError as err:
            raise CommandError(err)

    def _explore_storage(self):
        """Generator of all files contained in media storage."""
        path = DBBACKUP_MEDIA_PATH
        dirs = [path]
        while dirs:
            path = dirs.pop()
            subdirs, files = self.media_storage.listdir(path)
            for media_filename in files:
                yield os.path.join(path, media_filename)
            dirs.extend([os.path.join(path, subdir) for subdir in subdirs])

    def backup_mediafiles(self):
        """
        Create backup file and write it to storage.
        """
        # Create file name
        extension = "tar%s" % ('.gz' if self.compress else '')
        filename = utils.filename_generate(extension,
                                           servername=self.servername,
                                           content_type=self.content_type)

        tarball = self._create_tar(filename)

        if self.encrypt:
            encrypted_file = utils.encrypt_file(tarball, filename)
            tarball, filename = encrypted_file

        self.logger.debug("Backup size: %s", utils.handle_size(tarball))
        if self.path is None:
            self.write_to_storage(tarball, filename)
        else:
            self.storage.write_file(tarball, filename)
        return filename
