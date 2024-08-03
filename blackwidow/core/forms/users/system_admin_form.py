from blackwidow.core.forms.users.console_user_form import ConsoleUserForm
from blackwidow.core.models.roles.role import Role
from blackwidow.core.models.users.system_admin import SystemAdmin
from blackwidow.engine.decorators.utility import get_models_with_decorator
from blackwidow.engine.extensions.list_extensions import inserted_list
from config.apps import INSTALLED_APPS


class SystemAdminForm(ConsoleUserForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        business_roles = get_models_with_decorator('is_business_role', INSTALLED_APPS)
        self.fields['role'].choices = inserted_list(
            [(x.id, x.name) for x in Role.objects.all() if x.name not in business_roles], 0, ('', ' --'))

    class Meta(ConsoleUserForm.Meta):
        model = SystemAdmin
