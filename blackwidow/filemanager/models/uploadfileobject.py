import re
from collections import OrderedDict

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.query_utils import Q
from django.utils.safestring import mark_safe

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.filemanager.utils.file_utils import FileUtils

PROJECT_PATH = settings.PROJECT_PATH
STATIC_UPLOAD_ROOT = settings.STATIC_UPLOAD_ROOT

__author__ = 'Ziaul Haque'


@decorate(is_object_context,
          route(route='upload-files', group='File Manager', module=ModuleEnum.DeviceManager,
                display_name='View & Download Files', group_order=1, item_order=2))
class UploadFileObject(OrganizationDomainEntity):
    fileobject = models.ForeignKey('core.FileObject', null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=8000, null=True, default=None)
    category = models.CharField(max_length=254, null=True, default='')
    author = models.CharField(max_length=254, null=True, default='')
    original_name = models.CharField(max_length=8000, null=True, default=None)
    version = models.CharField(max_length=254, null=True, default=None)
    published_date = models.DateField(null=True)
    tags = models.ManyToManyField('filemanager.DocumentTag')

    class Meta:
        app_label = 'filemanager'

    @classmethod
    def success_url(cls):
        from blackwidow.filemanager.models import FileUploadManager
        return reverse(FileUploadManager.get_route_name(ViewActionEnum.Manage))

    @property
    def render_code(self):
        _url = reverse(self.get_route_name(ViewActionEnum.KeyInfo), kwargs={'pk': self.pk})
        return mark_safe(
            "<a class='inline-link load-keyinfo' data-title='" + self.title +
            "' href='" + _url + "' >" + self.code + "</a>")

    @property
    def render_published_date(self):
        return mark_safe('<div style="width: 150px">' + (
            self.published_date.strftime('%d/%m/%Y') if self.published_date else 'N/A') + '</div>')

    @property
    def render_author(self):
        return mark_safe('<div style="width: 150px">' + (self.author if self.author else 'N/A') + '</div>')

    @property
    def render_type_of_document(self):
        return mark_safe('<div style="width: 150px">' + (self.category if self.category else 'N/A') + '</div>')

    @classmethod
    def search_type_of_document(cls, queryset, values):
        values_list = values.split(',')
        or_query = None
        for value in values_list:
            q = Q(**{'category__icontains': value})
            if or_query is None:
                or_query = q
            else:
                or_query |= q
        return queryset.filter(or_query)

    @classmethod
    def table_columns(cls):
        return ['render_code', 'title:Name of document', 'render_author', 'render_published_date',
                'render_type_of_document', 'render_tags__or__keywords']

    @property
    def relative_url(self):
        return re.sub('(.)*' + STATIC_UPLOAD_ROOT.replace(PROJECT_PATH, '').replace('/', '\\/'),
                      '/static_media/uploads/', str(self.fileobject.file))

    @property
    def render_file_size(self):
        try:
            _size = getattr(self.fileobject, 'file').size
            return FileUtils.human_readable_file_size(size=_size)
        except Exception as e:
            return ""

    @property
    def render_file_type(self):
        if self.fileobject:
            return FileUtils.guess_file_type(file_obj=self.fileobject)
        return "N/A"

    @property
    def render_icon(self):
        _file_type = self.render_file_type
        return FileUtils.file_icon_detect(_file_type)

    @property
    def render_download_link(self):
        _url = reverse(self.get_route_name(ViewActionEnum.SecureDownload), kwargs={'pk': self.pk})
        _title = '<i class="fa fa-download" aria-hidden="true"></i>'
        return mark_safe('<a title="Click to download this item" href="' + _url + '" >' + _title + '</a>')

    @property
    def render_delete_link(self):
        _url = reverse(self.get_route_name(ViewActionEnum.Delete), kwargs={'ids': self.pk})
        _icon = '<i class="icon-remove"></i>'
        _delete_link = '<a class="manage-action all-action confirm-action" ' \
                       'title="Click to remove this item" data-action="delete" data-ajax="0" href="' + _url + '" >' \
                       + _icon + '</a>'
        return mark_safe(_delete_link)

    @property
    def render_filename(self):
        _url = reverse(self.get_route_name(ViewActionEnum.KeyInfo), kwargs={'pk': self.pk})
        return mark_safe(
            "<a class='inline-link load-keyinfo' data-title='" + self.title + "' href='" + _url + "' >"
            + self.render_icon + " " + self.original_name + "</a>")

    @property
    def details_config(self):
        details = OrderedDict()
        details['Code'] = self.code
        if self.is_image():
            details['Preview'] = self.render_image
        details['Name of document'] = self.title if self.title else "N/A"
        details['Author'] = self.author if self.author else "N/A"
        details['Published date'] = self.render_published_date
        details['Type of document'] = self.category if self.category else "N/A"
        details['Document Version'] = self.version if self.version else "N/A"
        details['Document Size'] = self.render_file_size
        details['Tags/ keywords'] = self.render_tags
        details['Uploaded By'] = self.last_updated_by
        details['Uploaded On'] = self.render_timestamp(self.date_created)
        return details

    def is_image(self):
        _file_type = self.render_file_type
        if _file_type in ['jpg', 'jpeg', 'gif', 'png']:
            return True
        return False

    @property
    def render_image(self):
        return mark_safe('<img class="thumbnail-border" src="' + str(self.fileobject.get_file_access_path()) + '">')

    @classmethod
    def search_filename(cls, queryset, values):
        value_list = values.split(',')
        or_query = None
        for _value in value_list:
            q = Q(**{"original_name__icontains": _value}) | Q(**{"fileobject__name__icontains": _value})
            if or_query is None:
                or_query = q
            else:
                or_query |= q
        return queryset.filter(or_query)

    @classmethod
    def order_by_filename(cls):
        return ['original_name', 'fileobject__name']

    @property
    def render_tags(self):
        if self.tags.exists():
            return mark_safe(', '.join([str(x) for x in self.tags.all()]))
        return "N/A"

    @property
    def render_tags__or__keywords(self):
        if self.tags.exists():
            return mark_safe(', '.join([str(x) for x in self.tags.all()]))
        return "N/A"

    @classmethod
    def search_tags__or__keywords(cls, queryset, value):
        value_list = value.replace(' ', ',').split(',')
        or_query = None
        for _value in value_list:
            if _value == '':
                continue
            q = Q(**{"tags__name__icontains": _value})
            if or_query is None:
                or_query = q
            else:
                or_query |= q
        return queryset.filter(or_query)

    @classmethod
    def sortable_columns(cls):
        return ['render_code', 'title', ]

    @classmethod
    def exclude_search_fields(cls):
        return ["render_published_date"]

    @classmethod
    def get_manage_buttons(cls):
        return []

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details, ViewActionEnum.SecureDownload]

    def details_link_config(self, **kwargs):
        return []
