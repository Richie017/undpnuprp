from django.db import transaction

from blackwidow.core.forms.users.console_user_form import ConsoleUserForm
from blackwidow.core.models.roles.role import Role
from undp_nuprp.nuprp_admin.models.users.mis_specialist import MISSpecialist

__author__ = 'Tareq'


class MISSpecialistForm(ConsoleUserForm):
    def save(self, commit=True):
        super().save(commit)
        with transaction.atomic():
            _role_name = MISSpecialist.get_model_meta('route', 'display_name') or MISSpecialist.__name__
            role = Role.objects.filter(name=_role_name).first()
            self.instance.role = role
            return self.instance

    def __init__(self, data=None, files=None, instance=None, **kwargs):
        kwargs.update({'address_level': 'Ward'})
        super().__init__(data=data, files=files, instance=instance, **kwargs)
        _role_name = MISSpecialist.get_model_meta('route', 'display_name') or MISSpecialist.__name__
        self.fields['role'].initial = Role.objects.filter(name=_role_name)[0].id

    class Meta(ConsoleUserForm.Meta):
        model = MISSpecialist
        fields = ['name', 'role']
