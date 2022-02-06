import os

from django.conf import settings
from openpyxl import Workbook

from blackwidow.core.models.file.exportfileobject import ExportFileObject
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.engine.file_handlers.aws_file_writer import AWSFileWriter
from config.aws_s3_config import MEDIA_DIRECTORY

EXPORT_FILE_ROOT = settings.EXPORT_FILE_ROOT


class GenericExporter(object):
    success_url = '/'

    def __init__(self, **kwargs):
        super(GenericExporter, self).__init__(**kwargs)

    @classmethod
    def export_to_excel(cls, queryset=None, model=None, filename=None, user=None, exporter_config=None, **kwargs):
        if hasattr(model, 'get_export_order_by') and model.get_export_order_by():
            queryset = queryset.order_by(model.get_export_order_by())
        exported_item = []
        path = os.path.join(EXPORT_FILE_ROOT)
        if not os.path.exists(path):
            os.makedirs(path)
        wb = Workbook()
        ws = wb.active
        ws.title = str(model.__name__)

        column_data = exporter_config.columns.all().order_by('date_created')
        ws, row_number = queryset.model.initialize_export(
            workbook=ws, row_number=1,
            columns=column_data,
            query_set=queryset, **kwargs
        )
        row_number += 1
        for obj in queryset:
            try:
                _pk, row_number = obj.export_item(workbook=ws, columns=column_data, row_number=row_number, **kwargs)
                exported_item.append(_pk)
            except Exception as exp:
                ErrorLog.log(exp)
        response = queryset.model.finalize_export(workbook=ws, row_number=row_number, query_set=queryset, **kwargs)

        dest_filename = filename
        generated_file_name = str(dest_filename) + '.xlsx'
        file_path = path + os.sep + generated_file_name
        wb.save(filename=file_path)

        # Uploading the exported file to AMAZON S3
        if settings.S3_STATIC_ENABLED:
            from config.aws_s3_config import STATIC_EXPORT_MEDIA_DIRECTORY
            try:
                with open(file_path, 'rb') as content_file:
                    content = content_file.read()
                    s3_file_name = STATIC_EXPORT_MEDIA_DIRECTORY + "/" + str(dest_filename) + '.xlsx'
                    file_path = s3_file_name.replace(MEDIA_DIRECTORY, '', 1)
                    AWSFileWriter.upload_file_with_content(file_name=s3_file_name, content=content)

                # after successfully upload to AWS S3, remove local file
                os.remove(file_path)
            except Exception as exp:
                ErrorLog.log(exp=exp)

        export_file_object = ExportFileObject()
        export_file_object.path = file_path
        export_file_object.name = dest_filename
        export_file_object.file = file_path
        export_file_object.extension = '.xlsx'
        export_file_object.organization = Organization.objects.first()
        export_file_object.save()

        return dest_filename, file_path
