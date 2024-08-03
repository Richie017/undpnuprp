from django.db import models

from blackwidow.core.models.common.custom_field import CustomFieldValue, CustomImageFieldValue, CustomDocumentFieldValue
from blackwidow.core.models.contracts.base import DomainEntity

__author__ = 'Tareq'


class DomainEntityMeta(DomainEntity):
    custom_field_values = models.ManyToManyField(CustomFieldValue)
    extra_images = models.ManyToManyField(CustomImageFieldValue)
    extra_documents = models.ManyToManyField(CustomDocumentFieldValue)

    @classmethod
    def get_serializer(cls):
        ss = DomainEntity.get_serializer()

        class Serializer(ss):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                from rest_framework import serializers

                if self.instance:
                    for cf_value in self.instance.custom_field_values.all():
                        self.fields[cf_value.field.name.lower()] = serializers.CharField(required=False, read_only=True,
                                                                                         max_length=200)

            class Meta(ss.Meta):
                model = cls
                fields = []

        return Serializer
