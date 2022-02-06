__author__ = 'ruddra'

from django.db import connection


def lock(self):
    cursor = connection.cursor()
    table = self.model._meta.db_table
    cursor.execute("LOCK TABLES %s WRITE" % table)
    row = cursor.fetchone()
    return row


def unlock(self):
    cursor = connection.cursor()
    table = self.model._meta.db_table
    cursor.execute("UNLOCK TABLES")
    row = cursor.fetchone()
    return row
