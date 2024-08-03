from django.db import transaction

from blackwidow.core.forms.users.console_user_form import ConsoleUserForm
from blackwidow.core.models.roles.role import Role
from undp_nuprp.nuprp_admin.models import MonitoringOfficial

__author__ = 'Ziaul Haque'


class MonitoringOfficialForm(ConsoleUserForm):
    def __init__(self, data=None, files=None, instance=None, **kwargs):
        kwargs.update({'address_level': 'Ward'})
        super(MonitoringOfficialForm, self).__init__(data=data, files=files, instance=instance, **kwargs)
        _role_name = MonitoringOfficial.get_model_meta('route', 'display_name') or MonitoringOfficial.__name__
        self.fields['role'].initial = Role.objects.filter(name=_role_name)[0].id

    def save(self, commit=True):
        super(MonitoringOfficialForm, self).save(commit)
        with transaction.atomic():
            _role_name = MonitoringOfficial.get_model_meta('route', 'display_name') or MonitoringOfficial.__name__
            role = Role.objects.filter(name=_role_name).first()
            self.instance.role = role
            return self.instance

    class Meta(ConsoleUserForm.Meta):
        model = MonitoringOfficial
        fields = ['name', 'role']
