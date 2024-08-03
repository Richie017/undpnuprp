import base64
import time
from random import choice
from string import ascii_uppercase

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.safestring import mark_safe
from rest_framework.serializers import ListSerializer

from blackwidow.core.models.common.location import Location
from blackwidow.core.models.file.fileobject import FileObject
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.utility import decorate, save_audit_log

STATIC_URL = settings.STATIC_URL

__author__ = 'ruddra, shamil'


@decorate(expose_api('image-uploads'), save_audit_log)
class ImageFileObject(FileObject):
    class Meta:
        proxy = True

    def __str__(self):
        _url = self.get_image_src_path()
        description = ""
        if self.description:
            description = self.description
        return mark_safe(
            '<a title="' + description + '" class="popup-thumbnail" href="' + _url +
            '"><img class="thumbnail-border" height="100" width="100" src="' + _url + '" /></a>')

    @property
    def relative_url(self):
        return self.get_image_src_path(allow_dummy_path=True)

    @property
    def render_image(self):
        return str(self)

    def get_image_src_path(self, allow_dummy_path=False):
        """
        This method returns image's accessible url. That means, the String returned by this method can be used as "src"
        attribute of an HTML img tag or as "src" url of Android image view etc.
        :param allow_dummy_path: If yes, the method may return a url that does not contain any image file. This is used
        to activate "graceful failure". So that, mobile app tries to get the content each and every time even if the
        object's last_updated is not changed. But for Mission Control, this should be False.
        :return: a String that can be used as src of image.
        """
        from settings import S3_STATIC_ENABLED
        _url = self.get_file_access_path()
        if _url and not S3_STATIC_ENABLED:
            _url = _url.replace('static_media/static_media/', 'static_media/')
        if _url is None:
            if allow_dummy_path:
                if self.path:
                    leading_slash = "/"
                    if S3_STATIC_ENABLED:
                        leading_slash = ""
                    return leading_slash + str(self.path)
            else:
                return STATIC_URL + 'img/dummy-photo.png'
        return _url

    @classmethod
    def table_columns(cls):
        return 'description', 'render_image', 'location', 'last_updated'

    @classmethod
    def get_serializer(cls):
        ss = FileObject.get_serializer()

        class ImageFileListSerializer(ListSerializer):
            @property
            def data(self):
                _data = super().data
                for item in _data:
                    item['file'] = item['relative_url']
                    del item['relative_url']
                return _data

            class Meta:
                model = cls
                fields = ('id', 'tsync_id', 'name', 'description', 'file', 'relative_url', 'location',
                          'generation_time', 'order', 'date_created', 'last_updated')

        class ImageFileSerializer(ss):
            location = Location.get_serializer()(required=False)

            def __init__(self, *args, fields=None, context=None, **kwargs):
                if bool(context):
                    if context['request'].data:
                        _data = context['request'].data
                        if 'base64_data' in _data:
                            base64_data = base64.b64decode(_data['base64_data'])  # saving decoded image to database
                            random_string = ''.join([choice(ascii_uppercase) for i in range(8)])
                            current_time = int(time.time()) * 1000
                            filename = "uploaded_image_%s_%s.png" % (current_time, random_string)
                            _data['file'] = ContentFile(base64_data, filename)
                            _data['name'] = filename
                            del _data['base64_data']
                super().__init__(*args, fields=fields, context=context, **kwargs)

            @property
            def data(self):
                _data = super(ImageFileSerializer, self).data
                _data['file'] = self.instance.relative_url
                return _data

            class Meta(ss.Meta):
                model = cls
                list_serializer_class = ImageFileListSerializer
                fields = ('id', 'tsync_id', 'name', 'description', 'file', 'relative_url', 'location',
                          'generation_time', 'order', 'date_created', 'last_updated')

        return ImageFileSerializer
