"""
    Created by shuvro on 28/05/18
"""

from django.core.management.base import BaseCommand

from blackwidow.core.models.file.exportfileobject import ExportFileObject

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        pg_survey_exported_queryset = ExportFileObject.objects.exclude(name__startswith='eligible').exclude(
            name__contains='_')

        print("Total {} files to be deleted".format(pg_survey_exported_queryset.count()))

        print(list(pg_survey_exported_queryset.values_list('name', flat=True)))

        com = input('Press "Y" to delete or any other key to exit:')
        if com.lower() == 'y':
            pg_survey_exported_queryset.delete()
            print('Successfully deleted the PG survey response exported files')
        else:
            print('Operation aborted!')
