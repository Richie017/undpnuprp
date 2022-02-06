"""
Restore media files.
"""
import tarfile

from dbbackup import utils
from dbbackup.management.commands import mediarestore


class Command(mediarestore.Command):
    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)

    def _upload_file(self, name, media_file):
        super(Command, self)._upload_file(name, media_file)

    def _restore_backup(self):
        self.logger.info("Restoring backup for media files")
        input_filename, input_file = self._get_backup_file(servername=self.servername)
        self.logger.info("Restoring: %s", input_filename)

        if self.decrypt:
            unencrypted_file, input_filename = utils.unencrypt_file(input_file, input_filename,
                                                                    self.passphrase)
            input_file.close()
            input_file = unencrypted_file

        self.logger.info("Backup size: %s", utils.handle_size(input_file))
        if self.interactive:
            self._ask_confirmation()

        input_file.seek(0)
        tar_file = tarfile.open(fileobj=input_file, mode='r:gz') \
            if self.uncompress \
            else tarfile.open(fileobj=input_file, mode='r:')
        # Restore file 1 by 1
        for media_file_info in tar_file:
            if media_file_info.path == 'media':
                continue  # Don't copy root directory
            media_file = tar_file.extractfile(media_file_info)
            if media_file is None:
                continue  # Skip directories
            name = media_file_info.path
            self._upload_file(name, media_file)
