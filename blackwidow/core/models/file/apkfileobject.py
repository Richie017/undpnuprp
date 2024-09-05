import os
import re

from django.db import models
from rest_framework import serializers

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from settings import APK_UPLOAD_ROOT, PROJECT_PATH, STATIC_UPLOAD_ROOT

__author__ = 'ziaul haque'


@decorate(is_object_context,
          route(route='apk-files', group='Import/Export', module=ModuleEnum.Settings, display_name="APK File"))
class ApplicationFileObject(OrganizationDomainEntity):
    name = models.CharField(max_length=8000, null=True, default=None)
    path = models.CharField(max_length=8000, null=True, default=None)
    extension = models.CharField(max_length=10, null=True, default=None)
    description = models.CharField(max_length=8000, null=True, default=None)
    file = models.FileField(default=None, max_length=8000, upload_to=STATIC_UPLOAD_ROOT,
                            null=True)

    @classmethod
    def all(cls):
        return ApplicationFileObject.objects.filter(file_type=cls.__name__)

    def __str__(self):
        return re.sub('.*' + APK_UPLOAD_ROOT.replace(PROJECT_PATH, '').replace('/', '\\/'),
                      '/static_media/fieldbuzz_applications/', str(self.file))

    @property
    def relative_url(self):
        return re.sub('(.)*' + APK_UPLOAD_ROOT.replace(PROJECT_PATH, '').replace('/', '\\/'),
                      '/static_media/fieldbuzz_applications/', str(self.file))

    def clean(self):
        self.type = self.__class__.__name__
        super().clean()

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
        super().save(*args, **kwargs)

    class Meta:
        app_label = 'core'

    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()

        class Serializer(ss):
            path = serializers.CharField(required=False, max_length=8000)
            extension = serializers.CharField(required=False, max_length=10)
            relative_url = serializers.CharField(read_only=True)

            class Meta(ss.Meta):
                model = cls

        return Serializer
