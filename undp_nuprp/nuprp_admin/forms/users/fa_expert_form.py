from django.db import transaction

from blackwidow.core.forms.users.console_user_form import ConsoleUserForm
from undp_nuprp.nuprp_admin.models.users.fa_expart import FAExpert

__author__ = 'Ziaul Haque'


class FAExpertForm(ConsoleUserForm):
    def __init__(self, data=None, files=None, instance=None, **kwargs):
        kwargs.update({'address_level': 'Pourashava/City Corporation'})
        super(FAExpertForm, self).__init__(data=data, files=files, instance=instance, **kwargs)

    def save(self, commit=True):
        with transaction.atomic():
            return super(FAExpertForm, self).save(commit)

    class Meta(ConsoleUserForm.Meta):
        model = FAExpert
        fields = ['name', 'role']
