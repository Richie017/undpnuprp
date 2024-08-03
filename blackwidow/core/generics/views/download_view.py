import os

from django.conf import settings
from django.shortcuts import redirect

from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.core.managers.archivemanager import ArchiveManager
from blackwidow.core.models import ErrorLog
from blackwidow.core.models.file.exportfileobject import ExportFileObject
from blackwidow.engine.extensions.clock import Clock
from blackwidow.engine.file_handlers.aws_file_writer import AWSFileWriter
from blackwidow.engine.file_handlers.file_path_handler import FilePathHandler
from config.aws_s3_config import MEDIA_DIRECTORY

EXPORT_FILE_ROOT = settings.EXPORT_FILE_ROOT
STATIC_EXPORT_URL = settings.STATIC_EXPORT_URL
S3_STATIC_ENABLED = settings.S3_STATIC_ENABLED


class GenericDownloadView(GenericListView):
    model_name = ExportFileObject

    def get(self, request, *args, **kwargs):
        models = list()
        path = os.path.join(EXPORT_FILE_ROOT)
        if not os.path.exists(path):
            os.makedirs(path)
        download_url = STATIC_EXPORT_URL
        if request.GET.get("names"):
            name_split = request.GET["names"].split(",")
            for name in name_split:
                export_file_objects = ExportFileObject.objects.filter(name=name)
                for export_file_object in export_file_objects:
                    export_file_object = export_file_objects.first()
                    if export_file_object not in models:
                        models += [export_file_object]
        else:
            if "pks" in kwargs:
                ids = kwargs["pks"].split(',')
                for _id in ids:
                    models += ExportFileObject.objects.filter(id=_id)
        if len(models) > 1:
            temporary_files = []
            if settings.S3_STATIC_ENABLED:
                for model in models:
                    # download files from S3
                    temporary_files.append(FilePathHandler.get_absolute_path(model.file))

            file_name = str(Clock.timestamp())
            ArchiveManager.zip_files([(x.path, x.name + x.extension) for x in models], os.path.join(path, file_name))

            # Uploading the exported file to AMAZON S3
            if settings.S3_STATIC_ENABLED:
                from config.aws_s3_config import STATIC_EXPORT_MEDIA_DIRECTORY
                try:
                    file_path = path + os.sep + str(file_name) + '.zip'
                    with open(file_path, 'rb') as content_file:
                        content = content_file.read()
                        s3_file_name = STATIC_EXPORT_MEDIA_DIRECTORY + "/" + str(file_name) + '.zip'
                        file_path = s3_file_name.replace(MEDIA_DIRECTORY, '', 1)
                        AWSFileWriter.upload_file_with_content(file_name=s3_file_name, content=content)
                    temporary_files.append(file_path)

                    # after successfully upload to AWS S3, remove local file
                    for temp_file in temporary_files:
                        try:
                            os.remove(temp_file)
                        except:
                            pass
                except Exception as exp:
                    ErrorLog.log(exp=exp)

            file_to_download = download_url + file_name + '.zip'
        else:
            current_timestamp = Clock.timestamp()
            if S3_STATIC_ENABLED:
                file_to_download = models[0].file.url + "?v=" + str(current_timestamp)
            else:
                file_name = models[0].name + models[0].extension
                file_to_download = download_url + file_name + "?v=" + str(current_timestamp)
        return redirect(file_to_download)
