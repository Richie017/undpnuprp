"""
    Created by tareq on 5/26/19
"""
from django.db import models
from rest_framework import serializers

from blackwidow.core.models.contracts.base import DomainEntity
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.utility import decorate

__author__ = "Tareq"


@decorate(expose_api('disabled-members-count'))
class DisabledMembersCount(DomainEntity):
    city = models.ForeignKey('core.Geography', on_delete=models.CASCADE)
    disability = models.CharField(blank=True, max_length=255)
    member_count = models.IntegerField(default=0)

    class Meta:
        app_label = 'reports'

    @classmethod
    def get_serializer(cls):
        DESerializer = DomainEntity.get_serializer()

        class PGMemberCountSerializer(DESerializer):
            city_name = serializers.SerializerMethodField()

            def get_city_name(self, obj):
                return obj.city.name

            class Meta:
                model = cls
                fields = 'city_name', 'disability', 'member_count', 'last_updated'

        return PGMemberCountSerializer
