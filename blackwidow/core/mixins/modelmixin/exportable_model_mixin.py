"""
    Written by tareq on 7/22/18
"""
import re

from blackwidow.engine.extensions import bw_titleize, Clock
from settings import SITE_ROOT

__author__ = 'Tareq'


class ExportableModelMixin(object):
    @classmethod
    def export_file_columns(cls):
        """
        this method is used to get the list of columns to be exported
        :return: a list of column properties
        """
        return list(cls.table_columns()) + list(cls.details_view_fields())

    @classmethod
    def export_tab_columns(cls):
        return []

    @classmethod
    def export_tab_items(cls, self):
        return []

    @classmethod
    def export_file_columns_title(cls):
        details_fields = cls.export_file_columns()
        file_columns_title = []
        for c in details_fields:
            _name = ''
            if ':' in c:
                _property, _name = c.split('>')[0].split(':')
            else:
                _property = c.split('>')[0]
            if not _name:
                if _property.startswith('render_'):
                    _name = bw_titleize(_property.replace('render_', ''))
                else:
                    _name = bw_titleize(_property)
            else:
                _name = bw_titleize(_name)

            if '>' in c:
                _name = c.split('>')[1] + ": " + _name

            file_columns_title.append(_name)

        return file_columns_title

    def export_file_column_items(self):
        _items = []
        details_fields = self.__class__.export_file_columns()
        for c in details_fields:
            if ':' in c:
                _property, _name = c.split('>')[0].split(':')
            else:
                _property = c.split('>')[0]

            _value = getattr(self, _property, '')

            if _property in self.__class__.get_datetime_fields():
                _value = self.render_timestamp(_value)

            _items.append(_value if _value else '')

        return _items

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        from blackwidow.core.models.config.exporter_config import ExporterConfig
        from blackwidow.core.models.config.exporter_column_config import ExporterColumnConfig

        ExporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        exporter_config, created = ExporterConfig.objects.get_or_create(
            model=cls.__name__, organization=organization)

        columns = list()
        column_index = 0

        details_fields = cls.export_file_columns()
        for c in details_fields:
            _name = ''
            if ':' in c:
                _property, _name = c.split('>')[0].split(':')
            else:
                _property = c.split('>')[0]
            if not _name:
                if _property.startswith('render_'):
                    _name = bw_titleize(_property.replace('render_', ''))
                else:
                    _name = bw_titleize(_property)
            else:
                _name = bw_titleize(_name)

            if '>' in c:
                _name = c.split('>')[1] + ": " + _name

            columns.append(
                ExporterColumnConfig(
                    column=column_index, column_name=_name, property_name=_property, ignore=False))
            column_index += 1

        # saving the column configs
        for c in columns:
            c.save(organization=organization, **kwargs)
            exporter_config.columns.add(c)

        return exporter_config

    @classmethod
    def initialize_export(cls, workbook=None, columns=None, row_number=None, query_set=None, **kwargs):
        """
        this method is used to format the excel file at the beginning of the export
        :param workbook: the workbook instance to work on
        :param columns: exported column configs
        :param row_number: beginning row at which the cursor is on
        :param query_set: the queryset for exportable objects
        :param kwargs: extra params
        :return: tuple of (workbook, row_number): these are updated workbook and row_number after the initialization
        """
        start_column = 1

        workbook.merge_cells(start_row=row_number, start_column=start_column, end_row=row_number,
                             end_column=start_column + 3)
        workbook.cell(row=row_number, column=start_column).value = kwargs.get(
            'export_file_title', bw_titleize(cls.__name__))

        row_number += 2

        column = 1
        for c in columns:
            workbook.cell(row=row_number, column=column).value = c.column_name
            column += 1

        for _col_name in cls.export_tab_columns():
            workbook.cell(row=row_number, column=column).value = bw_titleize(_col_name)
            column += 1

        return workbook, row_number

    def render_timestamp(self, value):
        _d = Clock.get_user_local_time(value).strftime("%d/%m/%Y - %I:%M %p")
        return _d

    def export_item(self, workbook=None, columns=None, row_number=None, **kwargs):
        """
        prepare individual row for the excel file
        :param workbook: the workbook instance to work on
        :param columns: exported column configs
        :param row_number: number of current row of cursor position
        :return: tuple (pk, row_number): pk of the current item, and the updated cursor position as row
        """
        for column in columns:
            _value = getattr(self, column.property_name, 'N/A')
            href = False

            if column.property_name in self.__class__.get_datetime_fields():
                _value = self.render_timestamp(_value)

            if _value:
                url_search = re.search('<a(.+?)href=(.+?)>(.+?)</a>', str(_value))
                if url_search:
                    _value = url_search.group(3)
                    _url = url_search.group(2).replace('"', '').replace("'", '')
                    href = True
            else:
                _value = ''

            href = False

            if href:
                workbook.cell(row=row_number, column=column.column + 1).value = '=HYPERLINK("{}", "{}")'.format(
                    (SITE_ROOT + _url), _value)
            else:
                workbook.cell(row=row_number, column=column.column + 1).value = str(_value)

        column_no = columns.last().column + 2 if columns.count() > 0 else 1

        for _value in self.__class__.export_tab_items(self):
            workbook.cell(row=row_number, column=column_no).value = str(_value)
            column_no += 1

        return self.pk, row_number + 1

    @classmethod
    def finalize_export(cls, workbook=None, row_number=None, query_set=None, **kwargs):
        """
        this method adds the final touches to
        :param workbook:
        :param row_number:
        :param query_set:
        :return:
        """
        start_column = 1
        row_number += 1

        workbook.merge_cells(start_row=row_number, start_column=start_column, end_row=row_number,
                             end_column=start_column + 3)
        workbook.cell(row=row_number, column=start_column).value = 'Generated by Field Buzz at ' + (
            Clock.now().strftime('%d-%m-%Y'))
        file_name = '%s_%s' % (cls.__name__, Clock.now().strftime('%d-%m-%Y'))
        return workbook, file_name
