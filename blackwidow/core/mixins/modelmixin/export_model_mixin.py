from blackwidow.core.models.config.exporter_config import ExporterConfig


class ExportModelMixin(object):
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
        for counter, field in enumerate(columns):
            workbook.cell(row=1, column=counter+1).value = field.column_name
        return workbook, 1

    @classmethod
    def finalize_export(cls, workbook=None, row_count=None, **kwargs):
        return workbook