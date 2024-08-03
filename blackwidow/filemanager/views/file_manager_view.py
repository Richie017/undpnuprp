from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.filemanager.forms import UploadFileObjectForm
from blackwidow.filemanager.models import FileUploadManager, UploadFileObject
from blackwidow.filemanager.utils.file_utils import FileUtils

__author__ = 'Ziaul Haque'


@decorate(override_view(model=FileUploadManager, view=ViewActionEnum.Manage))
class FileUploadManagerView(GenericListView):

    def get_template_names(self):
        return ['_file_upload.html']

    def get_context_data(self, **kwargs):
        context = super(FileUploadManagerView, self).get_context_data(**kwargs)
        all_files = UploadFileObject.objects.order_by('-date_created')
        _file_objects = list(map(FileUtils.file_serialize, all_files))
        context['file_objects'] = _file_objects
        context['form'] = UploadFileObjectForm()
        return context
