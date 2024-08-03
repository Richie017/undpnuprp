from django.core.management.base import BaseCommand
from django.db.models import Max

from blackwidow.core.models import ExportFileObject, ImportFileObject, ImageFileObject, FileObject
from blackwidow.engine.routers.database_router import BWDatabaseRouter

__author__ = 'Ziaul Haque'


class Command(BaseCommand):
    def handle(self, *args, **options):
        # ExportFileObject
        offset = 0
        limit = 1000

        queryset = ExportFileObject.all_objects.using(
            BWDatabaseRouter.get_write_database_name()
        ).filter(name__isnull=False).order_by('pk')
        max_id = queryset.aggregate(Max('pk'))['pk__max']
        max_processed_id = 0
        while max_processed_id < max_id:
            file_objects = queryset[offset:limit]
            updatable_entries = []
            for file_obj in file_objects:
                _file_obj_id = file_obj.pk
                max_processed_id = _file_obj_id
                name = file_obj.name.split('.')[0]
                extension = file_obj.extension
                _path = 'static_media/exported-files/' + name + extension
                file_obj.path = _path
                file_obj.file = _path
                updatable_entries.append(file_obj)

            entries_count = len(updatable_entries)
            if entries_count > 0:
                ExportFileObject.objects.bulk_update(updatable_entries)
                print("...updated {} ExportFileObject entries".format(entries_count))
            offset += 1000
            limit += 1000

        # ImportFileObject
        offset = 0
        limit = 1000

        queryset = ImportFileObject.all_objects.using(
            BWDatabaseRouter.get_write_database_name()
        ).filter(name__isnull=False).order_by('pk')
        max_id = queryset.aggregate(Max('pk'))['pk__max']
        max_processed_id = 0
        while max_processed_id < max_id:
            file_objects = queryset[offset:limit]
            updatable_entries = []
            for file_obj in file_objects:
                _file_obj_id = file_obj.pk
                max_processed_id = _file_obj_id
                name = file_obj.name.split('.')[0]
                extension = file_obj.extension
                _path = 'static_media/uploads/' + name + extension
                file_obj.path = _path
                file_obj.file = _path
                updatable_entries.append(file_obj)

            entries_count = len(updatable_entries)
            if entries_count > 0:
                ImportFileObject.objects.bulk_update(updatable_entries)
                print("...updated {} ImportFileObject entries".format(entries_count))
            offset += 1000
            limit += 1000

        # ImageFileObject
        offset = 0
        limit = 1000
        temp = 0
        queryset = ImageFileObject.all_objects.using(
            BWDatabaseRouter.get_write_database_name()
        ).filter(name__isnull=False).order_by('pk')
        max_id = queryset.aggregate(Max('pk'))['pk__max']
        max_processed_id = 0
        while max_processed_id < max_id:
            file_objects = queryset[offset:limit]
            updatable_entries = []
            for file_obj in file_objects:
                _file_obj_id = file_obj.pk
                max_processed_id = _file_obj_id
                _path = 'static_media/uploads/' + file_obj.name
                if len(file_obj.name.split('.')) == 1:
                    temp += 1
                file_obj.path = _path
                file_obj.file = _path
                updatable_entries.append(file_obj)

            entries_count = len(updatable_entries)
            if entries_count > 0:
                ImageFileObject.objects.bulk_update(updatable_entries)
                print("...updated {} ImageFileObject entries".format(entries_count))
            offset += 1000
            limit += 1000
        print("Temp: {}".format(temp))

        # FileObject
        offset = 0
        limit = 1000
        temp = 0
        queryset = FileObject.all_objects.using(
            BWDatabaseRouter.get_write_database_name()
        ).filter(name__isnull=False, type='FileObject').order_by('pk')
        max_id = queryset.aggregate(Max('pk'))['pk__max']
        max_processed_id = 0
        while max_processed_id < max_id:
            file_objects = queryset[offset:limit]
            updatable_entries = []
            for file_obj in file_objects:
                _file_obj_id = file_obj.pk
                max_processed_id = _file_obj_id
                _path = 'static_media/uploads/' + file_obj.name
                if len(file_obj.name.split('.')) == 1:
                    _path = 'static_media/uploads/' + file_obj.name + file_obj.extension
                    temp += 1
                file_obj.path = _path
                file_obj.file = _path
                print(_path)
                updatable_entries.append(file_obj)

            entries_count = len(updatable_entries)
            if entries_count > 0:
                FileObject.objects.bulk_update(updatable_entries)
                print("...updated {} FileObject entries".format(entries_count))
            offset += 1000
            limit += 1000
        print("Temp: {}".format(temp))
