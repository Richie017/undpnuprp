import os

from django.conf import settings
from django.urls.base import reverse
from django.utils.safestring import mark_safe

from blackwidow.core.models.file.fileobject import FileObject
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

EXPORT_FILE_ROOT = settings.EXPORT_FILE_ROOT
SITE_NAME = settings.SITE_NAME
S3_STATIC_ENABLED = settings.S3_STATIC_ENABLED

__author__ = 'Tareq'


@decorate(is_object_context,
          route(route='export-files', group='Import/Export',
                module=ModuleEnum.Settings, display_name="Exported File"))
class ExportFileObject(FileObject):
    class Meta:
        proxy = True

    @property
    def file_exists(self):
        """
        :return:
        """
        if S3_STATIC_ENABLED:
            return True
        _file_name = self.name + self.extension
        _file_path = os.path.join(EXPORT_FILE_ROOT, _file_name)
        return bool(os.path.exists(_file_path))

    @classmethod
    def all(cls):
        return FileObject.objects.filter(file_type=cls.__name__)

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Download, ViewActionEnum.Delete]

    @property
    def download_link(self):
        return mark_safe('<a class="inline-link" href="' + reverse(
            self.__class__.get_route_name(action=ViewActionEnum.Download),
            kwargs={'pks': self.pk}
        ) + '">' + self.name + self.extension + '</a>')

    def get_external_download_link(self, display_name=None):
        if not display_name:
            return self.download_link
        return mark_safe('<a class="inline-link" href="http://' + SITE_NAME + reverse(
            ExportFileObject.get_route_name(action=ViewActionEnum.Download), kwargs={
                'pks': self.pk}) + '">' + display_name + '</a>')
