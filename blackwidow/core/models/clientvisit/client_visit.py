from django.db import models
from rest_framework import serializers

from blackwidow.core.models.clients.client import Client
from blackwidow.core.models.common.location import Location
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'activehigh'


class VisitClient(OrganizationDomainEntity):
    client = models.ForeignKey(Client, null=True)
    location = models.OneToOneField(Location, null=True)
    visit_time = models.BigIntegerField(default=0)
    description = models.CharField(max_length=8000, default='')
    purpose = models.CharField(max_length=8000, null=True, blank=True)

    @property
    def render_visited_on(self):
        if self.visit_time > 0:
            return self.render_timestamp(self.visit_time)
        else:
            return self.render_timestamp(self.date_created)

    @classmethod
    def table_columns(cls):
        return 'code', 'created_by:Visited By', 'location', 'render_visit_time', 'last_updated:Sync Time'

    @classmethod
    def get_manage_buttons(cls):
        return []

    def details_link_config(self, **kwargs):
        return []

    @property
    def details_config(self):
        d = super().details_config

        custom_list = ['code', 'location']
        for key in d:
            if not key in custom_list:
                del d[key]
        d['Retailer'] = self.client
        d['Visited By'] = self.created_by
        d['Location'] = self.location
        d['Visit Time'] = self.render_timestamp(self.visit_time)
        d['Sync Time'] = self.render_timestamp(self.last_updated)
        return d

    @classmethod
    def default_order_by(cls):
        return "-code"

    @classmethod
    def get_datetime_fields(cls):
        return super().get_datetime_fields()  ## + ['visit_time']

    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()

        class Serializer(ss):
            location = Location.get_serializer()()
            description = serializers.CharField(required=False)

            class Meta(ss.Meta):
                model = cls
                fields = ('id', 'tsync_id', 'code', 'client', 'location', 'visit_time', 'description', 'purpose')

        return Serializer
