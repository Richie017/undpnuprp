from collections import OrderedDict

from blackwidow.core.models.contracts.configurabletype import ConfigurableType
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'Shuvro'


@decorate(is_object_context,
          route(route='training-participant', group='Descriptors',
                module=ModuleEnum.Settings, display_name="Training Participant", item_order=5))
class TrainingParticipant(ConfigurableType):
    class Meta:
        app_label = 'nuprp_admin'

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

