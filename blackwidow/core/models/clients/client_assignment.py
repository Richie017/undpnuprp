from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity


__author__ = 'Mahmud'

from django.apps import apps

get_model = apps.get_model


class ClientAssignment(OrganizationDomainEntity):
    clients = models.ManyToManyField('core.Client')
    client_type = models.CharField(max_length=200, default='')

    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()
        ct = get_model('core', 'ClientCompact')

        class Serializer(ss):
            clients = ct.get_serializer()(required=False, many=True)

            class Meta(ss.Meta):
                model = cls
                fields = ('id', 'code', 'clients', 'client_type')

        return Serializer

