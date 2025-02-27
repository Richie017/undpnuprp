from collections import OrderedDict

from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context, is_role_context, has_data_filter
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'Tareq'


@decorate(is_object_context, is_role_context, has_data_filter,
          route(route='town-authority', group='Users', module=ModuleEnum.Settings,
                display_name='Town Authority', group_order=1, item_order=5, hide=True))
class TownAuthority(ConsoleUser):
    @property
    def render_email_address(self):
        try:
            return self.emails.first().email
        except:
            return 'N/A'

    @property
    def render_city(self):
        try:
            return self.addresses.first().geography.name
        except AttributeError:
            return 'N/A'

    @classmethod
    def table_columns(cls):
        return (
            'render_code', 'name', 'render_email_address',
            'render_city', 'created_by', 'date_created', 'last_updated'
        )

    @property
    def details_config(self):
        details = OrderedDict()
        details['code'] = self.code
        details['name'] = self.name
        details['login'] = self.user.username
        details['email_address'] = self.render_email_address
        details['address'] = self.addresses.first()
        details['created_by'] = self.created_by
        details['created_on'] = self.render_timestamp(self.date_created)
        details['updated_on'] = self.render_timestamp(self.last_updated)
        return details

    class Meta:
        app_label = 'nuprp_admin'
        proxy = True
