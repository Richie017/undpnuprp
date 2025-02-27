from collections import OrderedDict

from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context, is_role_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = "Ziaul Haque"


@decorate(is_object_context, is_role_context,
          route(route='socioeconomic-nutrition-expert', group='Users', module=ModuleEnum.Settings,
                display_name='Socioeconomic & Nutrition Expert', group_order=1, item_order=8))
class SocioeconomicNutritionExpert(ConsoleUser):
    class Meta:
        app_label = 'nuprp_admin'
        proxy = True

    @property
    def render_email_address(self):
        try:
            return self.emails.first().email
        except:
            return 'N/A'

    @classmethod
    def table_columns(cls):
        return (
            'render_code', 'name', 'render_email_address',
            'created_by', 'date_created', 'last_updated'
        )

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete]

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

    @property
    def tabs_config(self):
        tabs = []
        return tabs
