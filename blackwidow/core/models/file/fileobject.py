from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from rest_framework import serializers

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

STATIC_UPLOAD_ROOT = settings.STATIC_UPLOAD_ROOT

__author__ = 'ActiveHigh, shamil'


class FileObject(OrganizationDomainEntity):
    name = models.CharField(max_length=8000, null=True, default=None)
    path = models.CharField(max_length=8000, null=True, default=None)
    extension = models.CharField(max_length=10, null=True, default=None)
    description = models.CharField(max_length=8000, null=True, default=None)
    file = models.FileField(default=None, max_length=8000, upload_to=STATIC_UPLOAD_ROOT, null=True, blank=True)
    location = models.ForeignKey('core.Location', null=True, on_delete=models.SET_NULL)
    generation_time = models.BigIntegerField(default=0)
    order = models.IntegerField(default=0)

    class Meta:
        app_label = 'core'

    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()

        class Serializer(ss):
            path = serializers.CharField(required=False, max_length=8000)
            extension = serializers.CharField(required=False, max_length=10)

            class Meta(ss.Meta):
                model = cls
                fields = [
                    'id', 'tsync_id', 'code', 'name', 'path', 'extension',
                    'description', 'file', 'date_created', 'last_updated'
                ]

        return Serializer

    def clean(self):
        self.type = self.__class__.__name__
        super(FileObject, self).clean()

    def __str__(self):
        if not self.path:
            return 'N/A'
        if self.name:
            name_part = self.name
        else:
            name_part = self.code

        try:
            from settings import S3_STATIC_ENABLED
            if S3_STATIC_ENABLED:
                download_link = self.file.url
            else:
                download_link = reverse(self.get_route_name(ViewActionEnum.Download), kwargs={'pks': self.pk})
            return mark_safe(name_part + ' (<a class="inline-link" href="' + download_link + '">Download</a>)')
        except:
            return mark_safe(name_part)

    def get_file_access_path(self):
        _url = None
        if self.file is not None and bool(self.file):
            leading_slash = "/"
            from settings import S3_STATIC_ENABLED
            if S3_STATIC_ENABLED:
                leading_slash = ""
            _url = leading_slash + str(self.file.url)
        return _url

    def get_choice_name(self):
        if self.code and self.name:
            return self.code + " : " + self.name
        elif self.code and not self.name:
            return self.code
        elif not self.code and self.name:
            return self.name
        else:
            return ''

    @property
    def serializable_fields(self):
        return ('name',) + super().serializable_fields

    def save(self, *args, **kwargs):
        self.file_type = self.__class__.__name__
        super(FileObject, self).save(*args, **kwargs)
