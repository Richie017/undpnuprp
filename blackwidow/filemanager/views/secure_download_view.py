import os

from django.conf import settings
from django.http import FileResponse
from django.shortcuts import redirect

from blackwidow.core.generics.views.details_view import GenericDetailsView
from blackwidow.core.models import ErrorLog
from blackwidow.engine.exceptions import BWException
from blackwidow.filemanager.models.uploadfileobject import UploadFileObject

S3_STATIC_ENABLED = settings.S3_STATIC_ENABLED

__author__ = 'Ziaul Haque'


class SecureFileDownloadView(GenericDetailsView):
    model_name = UploadFileObject

    @classmethod
    def generate_downloadable_content(cls, file_name, file_path, *args, **kwargs):
        _error_response = "Document \"{}\" that you are trying to download doesn't exist in system.".format(file_name)
        _response_class = FileResponse
        if os.path.isfile(file_path):
            try:
                _file_size = os.path.getsize(file_path)
                response = _response_class((line for line in open(file_path, 'rb')))
                response['Content-Disposition'] = "attachment; filename={0}".format(file_name)
                response['Content-Length'] = _file_size
                return response
            except Exception as err:
                ErrorLog.log(err)
                raise BWException(_error_response)
        else:
            raise BWException(_error_response)

    def get(self, request, *args, **kwargs):
        _document_pk = int(kwargs.get("pk", "0"))
        document_object = UploadFileObject.objects.filter(pk=_document_pk).first()
        if document_object:
            file_obj = document_object.fileobject
            _file_physical_path = file_obj.get_file_access_path()
            if S3_STATIC_ENABLED:
                return redirect(_file_physical_path)

            if _file_physical_path.startswith('/'):
                _file_physical_path = _file_physical_path.strip('/')

            _content_name = document_object.original_name if document_object.original_name else file_obj.name
            response = SecureFileDownloadView.generate_downloadable_content(
                file_name=_content_name, file_path=_file_physical_path
            )
            return response
        else:
            return FileResponse()
