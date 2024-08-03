from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.extensions.bw_titleize import bw_titleize


class SettingsItem(OrganizationDomainEntity):

    @classmethod
    def display_name(cls):
        name = cls.get_model_meta('route', 'display_name')
        if name is None:
            return bw_titleize(cls.__name__.replace('SettingsItem', ''))
        return name

    def format_value(self, value):
        if self.type != self.__class__.__name__:
            _c = self.to_subclass()
            return _c.format_value(value)
        return value

