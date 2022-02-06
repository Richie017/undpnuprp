from collections import OrderedDict

from blackwidow.core.models.contracts.configurabletype import ConfigurableType

__author__ = 'Ziaul Haque'


class Sector(ConfigurableType):
    class Meta:
        app_label = 'nuprp_admin'

    def get_choice_name(self):
        return self.name

    @classmethod
    def table_columns(cls):
        return 'code', 'name', 'last_updated'

    @property
    def details_config(self):
        details = OrderedDict()
        details['Code'] = self.code
        details['Name'] = self.name

        details['Last Updated By'] = self.last_updated_by if self.last_updated_by is not None else "N/A"
        details['Created On'] = self.render_timestamp(self.date_created)
        details['Last Updated On'] = self.render_timestamp(self.last_updated)
        return details
