import re

from rest_framework import serializers

from blackwidow.core.models.file.fileobject import FileObject
from blackwidow.engine.decorators.utility import decorate, is_object_context
from settings import STATIC_UPLOAD_ROOT, PROJECT_PATH

__author__ = 'ruddra'


@decorate(is_object_context)
class XmlFileObject(FileObject):
    class Meta:
        proxy = True

    @property
    def relative_url(self):
        return re.sub('(.)*' + STATIC_UPLOAD_ROOT.replace(PROJECT_PATH, '').replace('/', '\\/'),
                      '/static_media/uploads/', str(self.file))

    @classmethod
    def get_serializer(cls):
        ss = FileObject.get_serializer()

        class Serializer(ss):
            relative_url = serializers.CharField(read_only=True)

            class Meta(ss.Meta):
                model = cls

        return Serializer
