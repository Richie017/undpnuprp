import json

from django.http import HttpResponse, JsonResponse

from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.filemanager.forms.uploadfileobject_form import UploadFileObjectForm
from blackwidow.filemanager.utils.file_utils import FileUtils

__author__ = 'Ziaul Haque'


class FileUploaderView(GenericListView):

    def post(self, request, *args, **kwargs):
        try:
            form = UploadFileObjectForm(request.POST, request.FILES)
            if form.is_valid():
                file_obj = form.save()
                _table_row = FileUtils.prepare_table_row(file_obj)
                _serialize_obj = FileUtils.file_serialize(file_obj)
                return JsonResponse({
                    'success': True,
                    'table_row': _table_row,
                    'file': _serialize_obj
                })
            else:
                return HttpResponse(content=json.dumps(form.errors), status=400, content_type='application/json')
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': e
            })
