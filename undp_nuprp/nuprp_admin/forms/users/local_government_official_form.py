from django.db import transaction

from blackwidow.core.forms.users.console_user_form import ConsoleUserForm
from undp_nuprp.nuprp_admin.models.users.local_government_official import LocalGovernmentOfficial

__author__ = 'Ziaul Haque'


class LocalGovernmentOfficialForm(ConsoleUserForm):
    def __init__(self, data=None, files=None, instance=None, **kwargs):
        kwargs.update({'address_level': 'Pourashava/City Corporation'})
        super(LocalGovernmentOfficialForm, self).__init__(data=data, files=files, instance=instance, **kwargs)

    def save(self, commit=True):
        with transaction.atomic():
            return super(LocalGovernmentOfficialForm, self).save(commit)

    class Meta(ConsoleUserForm.Meta):
        model = LocalGovernmentOfficial
        fields = ['name', 'role']
