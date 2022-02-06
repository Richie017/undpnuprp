"""
Created by tareq on 3/29/18
"""

import random

from django.conf import settings

from blackwidow.engine.routers.pinning import this_thread_is_pinned

__author__ = 'Tareq'

DEFAULT_DB_ALIAS = 'default'
SLAVE_DATABASES_ALIAS = 'SLAVE_DATABASES'


class BWDatabaseRouter:
    @classmethod
    def get_read_database_name(cls):
        return getattr(settings, 'READ_DATABASE_NAME', DEFAULT_DB_ALIAS)

    @classmethod
    def get_export_database_name(cls):
        return getattr(settings, 'EXPORT_DATABASE_NAME', DEFAULT_DB_ALIAS)

    @classmethod
    def get_write_database_name(cls):
        return getattr(settings, 'WRITE_DATABASE_NAME', DEFAULT_DB_ALIAS)

    @classmethod
    def get_default_database_name(cls):
        return getattr(settings, 'WRITE_DATABASE_NAME', DEFAULT_DB_ALIAS)

    def get_slave(self):
        """Returns the alias of a slave database."""
        if hasattr(settings, SLAVE_DATABASES_ALIAS):
            # Shuffle the list so the first slave db isn't slammed during startup.
            slave_dbs = getattr(settings, SLAVE_DATABASES_ALIAS)
            if isinstance(slave_dbs, dict):
                try:
                    total_weight = sum(slave_dbs.values())
                    for db_key, weight in slave_dbs.items():
                        if random.uniform(0, 1) <= (weight * 1.0 / total_weight):
                            return db_key
                        total_weight -= weight
                except:
                    pass

            dbs = list(slave_dbs)
            return random.choice(dbs)
        else:
            slaves = list(settings.DATABASES.keys())
            slaves.remove(DEFAULT_DB_ALIAS)
            if len(slaves):
                return random.choice(slaves)
        return DEFAULT_DB_ALIAS

    def db_for_read(self, model, **hints):
        """Send reads to slaves in round-robin."""
        return DEFAULT_DB_ALIAS if this_thread_is_pinned() else self.get_slave()

    def db_for_write(self, model, **hints):
        """Send all writes to the master."""
        return DEFAULT_DB_ALIAS

    def allow_relation(self, obj1, obj2, **hints):
        """Allow all relations, so FK validation stays quiet."""
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == DEFAULT_DB_ALIAS

    def allow_syncdb(self, db, model):
        """Only allow syncdb on the master."""
        return db == DEFAULT_DB_ALIAS
