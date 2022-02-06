from django.db import models
from rest_framework import serializers

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.roles.role import Role
from blackwidow.core.models.users.user import ConsoleUser

__author__ = 'Mahmud'


class InfrastructureUserAssignment(OrganizationDomainEntity):
    users = models.ManyToManyField(ConsoleUser)
    role = models.ForeignKey(Role)

    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()

        class Serializer(ss):
            users = serializers.PrimaryKeyRelatedField(many=True, required=True, queryset=ConsoleUser.objects.all())
            role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())

            class Meta(ss.Meta):
                model = cls

        return Serializer