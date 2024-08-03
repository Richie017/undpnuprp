from django.db import models

from blackwidow.core.mixins.modelmixin.export_model_mixin import ExportModelMixin
from blackwidow.core.models.config.exporter_config import ExporterConfig
from blackwidow.core.models.config.importer_column_config import ImporterColumnConfig
from blackwidow.core.models.config.importer_config import ImporterConfig
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.clock import Clock

__author__ = 'activehigh'


class PerformanceIndex(OrganizationDomainEntity, ExportModelMixin):
    user = models.ForeignKey(ConsoleUser)
    start_time = models.BigIntegerField(default=0, null=True)
    end_time = models.BigIntegerField(default=0, null=True)
    name = models.CharField(max_length=500)
    target = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    achieved = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    @classmethod
    def get_datetime_fields(cls):
        return ['start_time', 'end_time'] + super().get_datetime_fields()

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete, ViewActionEnum.Export]

    @classmethod
    def get_queryset(cls, queryset=None, profile_filter=False, **kwargs):
        if profile_filter:
            _timestamp = Clock.timestamp()
            return queryset.filter(start_time__lte=_timestamp, end_time__gte=_timestamp)
        return queryset

    @classmethod
    def table_columns(cls):
        return 'code', 'user', 'start_time', 'end_time', 'target', 'achieved', 'is_active', 'last_updated'

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        """
        :param organization: the reference organization
        :param kwargs:
        :return: returns the exporter configuration for this class
        """
        exporter_configs = ExporterConfig.objects.filter(model=cls.__name__, organization=organization)
        if not exporter_configs.exists():
            exporter_config = ExporterConfig()
            exporter_config.save(**kwargs)
        else:
            for e in exporter_configs:
                e.delete()
            exporter_config = ExporterConfig()
            exporter_config.save(**kwargs)
        '''
        We are keeping the columns blank for now
        TO DO: will be replaced with actual dynamic codes to load columns from database configuration
        '''
        columns = []
        for c in columns:
            c.save(organization=organization, **kwargs)
            exporter_config.columns.add(c)
        return exporter_config

    def export_item(self, workbook=None, columns=None, row_number=None, **kwargs):
        """
        Called for each item, this function should write the rows directly into the work book
        :param workbook: the workbook to write to
        :param columns: columns returned from export_config
        :param row_number: the row index of the worksheet
        :return:
        """

        return 0, row_number + 1

    @classmethod
    def initialize_export(cls, workbook=None, columns=None, row_count=None, **kwargs):
        return workbook, 1

    @classmethod
    def finalize_export(cls, workbook=None, row_count=None, **kwargs):
        return workbook

    @classmethod
    def importer_config(cls, organization=None, **kwargs):
        importer_config, result = ImporterConfig.objects.get_or_create(model=cls.__name__, organization=organization,
                                                                       starting_row=4)
        if result or importer_config.columns.count() == 0:
            importer_config.save(**kwargs)
        else:
            for items in importer_config.columns.all():
                items.delete()
        columns = [
            ImporterColumnConfig(column=1, column_name='ID', property_name='id', ignore=False),
            ImporterColumnConfig(column=2, column_name='Name', property_name='name', ignore=False),
        ]
        for i in range(1, 47):
            columns += [ImporterColumnConfig(column=i + 2, column_name='value', property_name='value', ignore=False)]
        for c in columns:
            c.save(organization=organization, **kwargs)
            importer_config.columns.add(c)
        return importer_config

    @classmethod
    def import_item(cls, config, sorted_columns, data, user=None, **kwargs):
        print(data)
        return data

    class Meta:
        abstract = True


class MonthlyKPI(PerformanceIndex):
    month = models.IntegerField(default=1)
    month_name = models.CharField(default="January", max_length=200)

    class Meta:
        abstract = True


class WeeklyKPI(PerformanceIndex):
    week = models.IntegerField(default=1)

    class Meta:
        abstract = True


class YearlyKPI(PerformanceIndex):
    year = models.IntegerField(default=2000)

    class Meta:
        abstract = True
