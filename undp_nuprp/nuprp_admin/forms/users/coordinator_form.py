from django.db import transaction

from blackwidow.core.forms.users.console_user_form import ConsoleUserForm
from undp_nuprp.nuprp_admin.models.users.coordinator import Coordinator

__author__ = 'Ziaul Haque'


class CoordinatorForm(ConsoleUserForm):
    def __init__(self, data=None, files=None, instance=None, **kwargs):
        kwargs.update({'address_level': 'Pourashava/City Corporation'})
        super(CoordinatorForm, self).__init__(data=data, files=files, instance=instance, **kwargs)

    def save(self, commit=True):
        with transaction.atomic():
            return super(CoordinatorForm, self).save(commit)

    class Meta(ConsoleUserForm.Meta):
        model = Coordinator
        fields = ['name', 'role']
