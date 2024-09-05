from collections import OrderedDict

from django.db import models

from blackwidow.core.models.contracts.configurabletype import ConfigurableType

__author__ = 'Ziaul Haque'


class SubSector(ConfigurableType):
    parent = models.ForeignKey('nuprp_admin.Sector', null=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'nuprp_admin'

    @property
    def select2_string(self):
        return str(self.name)

    def to_json(self, depth=0, expand=None, wrappers=[], conditional_expand=[], **kwargs):
        obj = super(SubSector, self).to_json(depth=0, expand=None, wrappers=[], conditional_expand=[], **kwargs)
        obj['select2_string'] = self.select2_string
        return obj

    def get_choice_name(self):
        return self.name

    @classmethod
    def table_columns(cls):
        return 'code', 'name', 'parent:Sector', 'last_updated'

    @property
    def details_config(self):
        details = OrderedDict()
        details['Code'] = self.code
        details['Name'] = self.name
        details['Sector'] = self.parent

        details['Last Updated By'] = self.last_updated_by if self.last_updated_by is not None else "N/A"
        details['Created On'] = self.render_timestamp(self.date_created)
        details['Last Updated On'] = self.render_timestamp(self.last_updated)
        return details
