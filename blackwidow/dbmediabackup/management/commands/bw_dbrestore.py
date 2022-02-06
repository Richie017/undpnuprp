"""
Restore database.
"""

from dbbackup.management.commands import dbrestore


class Command(dbrestore.Command):
    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)

    def _get_database(self, options):
        return super(Command, self)._get_database(options)

    def _restore_backup(self):
        super(Command, self)._restore_backup()
