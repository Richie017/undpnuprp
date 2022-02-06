from django.db import models
from rest_framework import serializers

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.utility import decorate, is_object_context

__author__ = 'activehigh'


@decorate(is_object_context, )
class OtherActivity(OrganizationDomainEntity):
    subject = models.CharField(max_length=200, default='')
    description = models.CharField(max_length=500, default='')

    @classmethod
    def table_columns(cls):
        return 'code', 'subject', 'description'

    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()

        class ODESerializer(ss):
            name = serializers.CharField(required=False)

            class Meta:
                model = cls
                read_only_fields = ss.Meta.read_only_fields

        return ODESerializer
