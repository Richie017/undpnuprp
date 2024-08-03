import re
from math import log2

from django.utils.safestring import mark_safe

__author__ = 'Ziaul Haque'


class FileUtils(object):

    @staticmethod
    def human_readable_file_size(size):
        _suffixes = ['bytes', 'KB', 'MB', 'GB', 'TB', 'EB', 'ZB']
        order = int(log2(size) / 10) if size else 0
        return '{:.3g} {}'.format(size / (1 << (order * 10)), _suffixes[order])

    @staticmethod
    def guess_file_type(file_obj):
        _type = 'application/file'
        _filename = getattr(file_obj, 'file').name
        if _filename:
            _type = _filename.split('.')[-1]
        if _type == 'docx':
            _type = 'application/microsoft-word'
        elif _type == 'pdf':
            _type = 'application/pdf'
        elif _type == 'xlsx':
            _type = 'application/Excel-worksheet'

        return _type

    @staticmethod
    def file_icon_detect(file_type=None):
        file_type = file_type.lower()
        _css_class = '	fa fa-file-o'
        if file_type in ['jpeg', 'jpg', 'gif', 'png']:
            _css_class = 'fa fa-file-image-o'
        elif file_type == 'application/pdf':
            _css_class = 'fa fa-file-pdf-o'
        elif file_type == 'text/plain':
            _css_class = 'fa fa-file-text-o'
        elif file_type == 'application/microsoft-word':
            _css_class = 'fa fa-file-word-o'
        elif file_type in ['application/x-zip-compressed', 'application/zip', 'application/x-tar']:
            _css_class = 'fa fa-file-zip-o'
        elif file_type == 'application/powerpoint-presentation':
            _css_class = 'fa fa-file-powerpoint-o'
        elif file_type == 'application/Excel-worksheet':
            _css_class = 'fa fa-file-excel-o'
        elif file_type == 'video/mp4':
            _css_class = 'fa fa-file-video-o'
        elif file_type in ['audio/mpeg']:
            _css_class = 'fa fa-file-audio-o'
        icon_class = '<i class="' + _css_class + '" style="font-size:20px;color:#00a99d;"></i>'
        return mark_safe(icon_class)

    @classmethod
    def order_name(cls, name):
        """order_name -- Limit a text to 20 chars length, if necessary strips the
        middle of the text and substitute it for an ellipsis.
        name -- text to be limited.
        """
        name = re.sub(r'^.*/', '', name)
        if len(name) <= 20:
            return name
        return name[:10] + "..." + name[-7:]

    @classmethod
    def file_serialize(cls, instance, file_attr='file'):
        """serialize -- Serialize a file instance into a dict.
        instance -- file instance
        file_attr -- attribute name that contains the FileField or ImageField
        """
        obj = getattr(instance.fileobject, file_attr)
        return {
            'id': instance.pk,
            'icon': instance.render_icon,
            'title': instance.title,
            'category': instance.category,
            'name': cls.order_name(obj.name),
            'filename': instance.render_filename,
            'type': instance.render_file_type,
            'size': instance.render_file_size,
            'version': instance.version,
            'description': instance.fileobject.description,
            'url': obj.url,
            'author': instance.author,
            'publish_date': instance.render_published_date,
            'download_link': instance.render_download_link,
            'delete_link': instance.render_delete_link,
            'tags': instance.render_tags
        }

    @classmethod
    def prepare_table_row(cls, instance):
        file_obj = cls.file_serialize(instance)
        table_row = '<tr>'
        table_row += '<td>' + str(file_obj["title"]) + '</td>'
        table_row += '<td>' + str(file_obj["author"]) + '</td>'
        table_row += '<td>' + str(file_obj["publish_date"]) + '</td>'
        table_row += '<td>' + str(file_obj["category"]) + '</td>'
        table_row += '<td>' + str(file_obj["tags"]) + '</td>'
        table_row += '<td>' + str(file_obj["size"]) + '</td>'
        table_row += '<td>' + str(file_obj["download_link"]) + ' ' + str(file_obj["delete_link"]) + '</td>'
        table_row += '</tr>'
        return table_row
