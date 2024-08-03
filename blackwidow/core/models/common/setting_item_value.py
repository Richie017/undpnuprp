from django.db import models

from blackwidow.core.models.common.settings_item import SettingsItem
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.extensions.bw_titleize import bw_titleize

__author__ = 'Tareq'


class SettingsItemValue(OrganizationDomainEntity):
    value = models.CharField(max_length=500)
    settings_item = models.ForeignKey(SettingsItem)

    @classmethod
    def get_dependent_field_list(cls):
        return []

    @property
    def render_settings(self):
        return bw_titleize(self.settings_item.type.replace('SettingsItem', ''))

    @property
    def render_value(self):
        return self.settings_item.format_value(self.value)

    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()

        class Serializer(ss):
            settings_item = SettingsItem

            class Meta(OrganizationDomainEntity.Meta):
                model = cls
                fields = ('id', 'code', 'value', 'settings_item', 'date_created')

        return Serializer

    @classmethod
    def table_columns(cls):
        return 'render_settings', 'render_value'
