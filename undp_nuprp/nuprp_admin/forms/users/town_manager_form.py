from django.db import transaction

from blackwidow.core.forms.users.console_user_form import ConsoleUserForm
from blackwidow.core.models.roles.role import Role
from undp_nuprp.nuprp_admin.models.users.town_manager import TownManager

__author__ = 'Tareq'


class TownManagerForm(ConsoleUserForm):
    def save(self, commit=True):
        super().save(commit)
        with transaction.atomic():
            _role_name = TownManager.get_model_meta('route', 'display_name') or TownManager.__name__
            role = Role.objects.filter(name=_role_name).first()
            self.instance.role = role
            return self.instance

    def __init__(self, data=None, files=None, instance=None, **kwargs):
        kwargs.update({'address_level': 'Pourashava/City Corporation'})
        super().__init__(data=data, files=files, instance=instance, **kwargs)
        _role_name = TownManager.get_model_meta('route', 'display_name') or TownManager.__name__
        self.fields['role'].initial = Role.objects.filter(name=_role_name)[0].id

    class Meta(ConsoleUserForm.Meta):
        model = TownManager
        fields = ['name', 'role']
