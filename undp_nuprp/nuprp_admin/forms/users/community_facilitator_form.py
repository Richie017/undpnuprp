from django.db import transaction

from blackwidow.core.forms.users.console_user_form import ConsoleUserForm
from blackwidow.core.models.roles.role import Role
from undp_nuprp.nuprp_admin.models.users.community_facilitator import CommunityFacilitator

__author__ = 'Tareq, Ziaul Haque'


class CommunityFacilitatorForm(ConsoleUserForm):

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        kwargs.update({'address_level': 'Ward'})
        super(CommunityFacilitatorForm, self).__init__(
            data=data, files=files, instance=instance, prefix=prefix, **kwargs)

    def save(self, commit=True):
        with transaction.atomic():
            self.instance = super(CommunityFacilitatorForm, self).save(commit)
            _role_name = CommunityFacilitator.get_model_meta('route', 'display_name') or CommunityFacilitator.__name__
            role = Role.objects.filter(name=_role_name).first()

            self.instance.role = role
            self.instance.save()
            return self.instance

    class Meta(ConsoleUserForm.Meta):
        model = CommunityFacilitator
        fields = ['name', 'role']
