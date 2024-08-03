from collections import OrderedDict
from datetime import datetime

from blackwidow.core.managers.modelmanager import DomainEntityModelManager
from blackwidow.core.models.config.exporter_column_config import ExporterColumnConfig
from blackwidow.core.models.config.exporter_config import ExporterConfig
from blackwidow.core.models.config.importer_column_config import ImporterColumnConfig
from blackwidow.core.models.config.importer_config import ImporterConfig
from blackwidow.core.models.geography.geography import Geography
from blackwidow.core.models.geography.geography_level import GeographyLevel
from blackwidow.engine.decorators.enable_export import enable_export
from blackwidow.engine.decorators.enable_import import enable_import
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.clock import Clock
from blackwidow.engine.routers.database_router import BWDatabaseRouter

__author__ = 'Tareq'


@decorate(is_object_context, enable_export, enable_import,
          route(route='all-geography', group='Address', group_order=2, item_order=1, module=ModuleEnum.Settings,
                display_name="Geography"))
class AllGeography(Geography):
    objects = DomainEntityModelManager(filter={'geography__isnull': True})

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(AllGeography, self).__init__(*args, **kwargs)
        levels = GeographyLevel.objects.all().order_by('-date_created').values_list('name', flat=True)

        entry = self
        level_index = 0
        while entry is not None and level_index < len(levels):
            level_name = entry.level.name
            self.__setattr__(level_name, entry)
            level_index += 1
            entry = entry.parent

    @classmethod
    def table_columns(cls):
        levels = GeographyLevel.objects.all().order_by('date_created').values_list('name', flat=True)
        return tuple(levels) + ('last_updated',)

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.AdvancedExport, ViewActionEnum.AdvancedImport]

    @classmethod
    def get_object_inline_buttons(cls):
        return []

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Download Excel"
        elif button == ViewActionEnum.AdvancedImport:
            return "Import Excel"

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        ExporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        exporter_config, created = ExporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)

        columns = list()
        column_index = 0
        level_queryset = GeographyLevel.objects.using(
            BWDatabaseRouter.get_export_database_name()
        ).all().order_by('date_created')
        for level in level_queryset:
            columns.append(
                ExporterColumnConfig(
                    column=column_index + 1, column_name=level.name + ' Code',
                    property_name=level.name.lower() + '_code', ignore=False
                )
            )
            columns.append(
                ExporterColumnConfig(
                    column=column_index, column_name=level.name,
                    property_name=level.name.lower(), ignore=False
                )
            )
            column_index += 2

        for c in columns:
            c.save(organization=organization, **kwargs)
            exporter_config.columns.add(c)

        return exporter_config

    def export_item(self, workbook=None, columns=None, row_number=None, **kwargs):
        return self.pk, row_number + 1

    @classmethod
    def initialize_export(cls, workbook=None, columns=None, query_set=None, **kwargs):
        geography_levels = GeographyLevel.objects.using(
            BWDatabaseRouter.get_export_database_name()
        ).values('name', 'id').order_by('date_created')

        geography_level_dict = OrderedDict()
        geography_raw_dict = OrderedDict()
        geography_dict = OrderedDict()
        for index, level in enumerate(geography_levels):
            _level_name = level['name']
            _level_id = level['id']
            geography_level_dict[_level_name] = index + 1

            geography_raw_dict[_level_id] = Geography.objects.using(BWDatabaseRouter.get_export_database_name()).filter(
                level_id=_level_id
            ).order_by('-date_created').values(
                'id', 'short_code', 'name', 'parent',
                'parent__level_id', 'level_id', 'level__name',
            )

        for index, level in enumerate(geography_levels):
            _level_id = level['id']
            _level_name = level['name']
            queryset = geography_raw_dict[_level_id]
            for item in queryset:
                if _level_id not in geography_dict.keys():
                    geography_dict[_level_id] = OrderedDict()
                geography_dict[_level_id][item['id']] = item

        row = 1
        column = 1
        for level in geography_levels:
            _level_name = level['name']
            workbook.cell(row=row, column=column).value = _level_name + ' Code'
            workbook.cell(row=row, column=column + 1).value = _level_name
            column += 2
        row += 1

        exportable_items = cls.objects.order_by('-date_created').values(
            'id', 'short_code', 'name', 'parent',
            'parent__level_id', 'level_id', 'level__name',
        )
        for entry in exportable_items:
            column = geography_level_dict[entry['level__name']] * 2
            current = entry
            while current is not None and column > 0:
                workbook.cell(row=row, column=column).value = current['name']
                column -= 1
                workbook.cell(row=row, column=column).value = current['short_code']
                column -= 1
                if current['parent__level_id'] and current['parent'] in geography_dict[current['parent__level_id']]:
                    current = geography_dict[current['parent__level_id']][current['parent']]
                else:
                    current = None
            row += 1
        return workbook, row

    @classmethod
    def finalize_export(cls, workbook=None, row_count=None, **kwargs):
        file_name = '%s_%s' % (cls.__name__, Clock.timestamp())
        return workbook, file_name

    @classmethod
    def importer_config(cls, organization=None, **kwargs):
        ImporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        importer_config, result = ImporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)
        importer_config.starting_row = 1
        importer_config.starting_column = 0
        importer_config.save(**kwargs)

        columns = list()
        column = 0
        for level in GeographyLevel.objects.all().order_by('date_created'):
            columns.append(ImporterColumnConfig(
                column=column + 1, column_name=level.name + ' Code', property_name=level.name.lower() + '_code',
                ignore=False))
            columns.append(ImporterColumnConfig(
                column=column, column_name=level.name, property_name=level.name.lower(), ignore=False))
            column += 2

        for c in columns:
            c.save(organization=organization, **kwargs)
            importer_config.columns.add(c)
        return importer_config

    @classmethod
    def import_item(cls, config, sorted_columns, data, user=None, **kwargs):
        return data

    @classmethod
    def post_processing_import_completed(cls, items=[], user=None, organization=None, **kwargs):
        def get_parent_from_dict(_g_dict, row, index):
            i = 0
            parent_id = None
            while i < index:
                col = i * 2
                name = str(row[str(col + 1)]) if row[str(col + 1)] else ''
                parent_id = _g_dict[name, parent_id] if (name, parent_id) in _g_dict.keys() else None
                i += 1
            return parent_id

        geography_levels = GeographyLevel.objects.all().order_by('date_created').values('pk', 'name')
        geography_dict = dict()
        current_timestamp = int(datetime.now().timestamp()) * 1000

        index = 0
        while index < len(geography_levels):
            level_id = geography_levels[index]['pk']
            existing_queryset = Geography.objects.filter(level_id=level_id).values(
                'pk', 'name', 'short_code', 'parent_id')
            for eq in existing_queryset:
                geography_dict[eq['name'], eq['parent_id']] = eq['pk']

            creatable_list = list()
            column = index * 2
            for item in items:
                geography_code = str(item[str(column)]) if item[str(column)] else ''
                geography_name = str(item[str(column + 1)]) if item[str(column + 1)] else ''

                if not geography_name:
                    continue

                modified_item = item
                if geography_levels[index]['name'] == "Ward" and len(geography_name) == 1:
                    if geography_name == "0":
                        continue
                    geography_name = "0" + geography_name
                    modified_item[str(column + 1)] = geography_name

                geo_parent_id = get_parent_from_dict(geography_dict, modified_item, index)
                geo_id = geography_dict[
                    geography_name, geo_parent_id] if (geography_name, geo_parent_id) in geography_dict.keys() else None
                if not geo_id:
                    geography = Geography(name=geography_name, parent_id=geo_parent_id, level_id=level_id,
                                          type=geography_levels[index]['name'], organization=organization,
                                          date_created=current_timestamp, last_updated=current_timestamp)
                    current_timestamp += 1
                    if geography_code:
                        geography.short_code = geography_code

                    creatable_list.append(geography)
                    geography_dict[geography_name, geo_parent_id] = -1
            Geography.objects.bulk_create(creatable_list)

            if index < len(geography_levels) - 1:
                existing_queryset = Geography.objects.using(BWDatabaseRouter.get_default_database_name()).filter(
                    level_id=level_id).values(
                    'pk', 'name', 'short_code', 'parent_id')
                for eq in existing_queryset:
                    geography_dict[eq['name'], eq['parent_id']] = eq['pk']
            index += 1

        Geography.generate_missing_codes()
