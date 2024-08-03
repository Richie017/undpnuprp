"""
Created by tareq on 7/25/17
"""
from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators import save_audit_log
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.utility import decorate

__author__ = 'Tareq'


@decorate(save_audit_log, expose_api('field-group'))
class FieldGroup(OrganizationDomainEntity):
    parent = models.ForeignKey('core.FieldGroup', null=True, on_delete=models.SET_NULL)
    assigned_code = models.CharField(max_length=128, blank=True)
    name = models.CharField(max_length=200)
    name_bd = models.CharField(max_length=200, blank=True)
    weight = models.IntegerField(default=100)

    class Meta:
        app_label = 'core'

    @classmethod
    def get_serializer(cls):
        _ODESerializer = OrganizationDomainEntity.get_serializer()

        class Serializer(_ODESerializer):
            class Meta(_ODESerializer.Meta):
                model = cls
                fields = (
                    'id', 'name', 'name_bd', 'parent', 'weight', 'date_created', 'last_updated'
                )

        return Serializer
