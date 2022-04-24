from blackwidow.engine.decorators.utility import is_role_context
from blackwidow.engine.decorators.utility import is_object_context
from blackwidow.engine.decorators.utility import save_audit_log
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.bwroles.models.users.customization.admin_modelbase import AdminModelBase
from blackwidow.engine.decorators.utility import decorate

__author__='__auto_generated__'


@decorate(is_role_context,is_object_context,save_audit_log,route(route="admin", group="Users", module=ModuleEnum.Administration,display_name="Admin"),expose_api("admin"))
class Admin(AdminModelBase):

    class Meta:
        proxy=True