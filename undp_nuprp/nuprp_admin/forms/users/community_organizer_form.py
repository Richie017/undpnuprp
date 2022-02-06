from django.db import transaction

from blackwidow.core.forms.users.console_user_form import ConsoleUserForm
from undp_nuprp.nuprp_admin.models.users.community_organizer import CommunityOrganizer

__author__ = 'Ziaul Haque'


class CommunityOrganizerForm(ConsoleUserForm):
    def __init__(self, data=None, files=None, instance=None, **kwargs):
        kwargs.update({'address_level': 'Ward'})
        super(CommunityOrganizerForm, self).__init__(data=data, files=files, instance=instance, **kwargs)

    def save(self, commit=True):
        with transaction.atomic():
            return super(CommunityOrganizerForm, self).save(commit)

    class Meta(ConsoleUserForm.Meta):
        model = CommunityOrganizer
        fields = ['name', 'role']
