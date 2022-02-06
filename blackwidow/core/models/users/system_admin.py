from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_role_context, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'Tareq'


@decorate(is_role_context, is_object_context,
          route(route='system-admins', group='Users', group_order=1, item_order=100,
                module=ModuleEnum.Settings, display_name='Other User'))
class SystemAdmin(ConsoleUser):
    class Meta:
        proxy = True
