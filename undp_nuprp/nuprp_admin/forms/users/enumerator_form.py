from django.db import transaction

from blackwidow.core.forms.users.console_user_form import ConsoleUserForm
from blackwidow.core.models.roles.role import Role
from undp_nuprp.nuprp_admin.models.users.enumerator import Enumerator

__author__ = 'Tareq'


class EnumeratorForm(ConsoleUserForm):
    def save(self, commit=True):
        super().save(commit)
        with transaction.atomic():
            _role_name = Enumerator.get_model_meta('route', 'display_name') or Enumerator.__name__
            role = Role.objects.filter(name=_role_name).first()
            self.instance.role = role

            if not self.instance.assigned_code:
                ward = self.instance.addresses.first().geography
                city = ward.parent
                index = Enumerator.all_objects.filter(addresses__geography__parent_id=city.pk).count()
                ward_name = ward.name
                if len(ward.name) < 2:
                    ward_name = '0' + ward.name
                elif len(ward.name) > 2:
                    ward_name = ward.name[:2]
                city_name = city.short_code
                self.instance.assigned_code = '%2s%2s%03d' % (city_name, ward_name, index)
                self.instance.save()
            return self.instance

    def __init__(self, data=None, files=None, instance=None, **kwargs):
        kwargs.update({'address_level': 'Ward'})
        super().__init__(data=data, files=files, instance=instance, **kwargs)
        _role_name = Enumerator.get_model_meta('route', 'display_name') or Enumerator.__name__
        self.fields['role'].initial = Role.objects.filter(name=_role_name)[0].id

    class Meta(ConsoleUserForm.Meta):
        model = Enumerator
        fields = ['name', 'role']
