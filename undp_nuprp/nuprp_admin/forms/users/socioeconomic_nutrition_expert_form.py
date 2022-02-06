from django.db import transaction

from blackwidow.core.forms.users.console_user_form import ConsoleUserForm
from undp_nuprp.nuprp_admin.models.users.socioeconomic_nutrition_expert import SocioeconomicNutritionExpert

__author__ = 'Ziaul Haque'


class SocioeconomicNutritionExpertForm(ConsoleUserForm):
    def __init__(self, data=None, files=None, instance=None, **kwargs):
        kwargs.update({'address_level': 'Pourashava/City Corporation'})
        super(SocioeconomicNutritionExpertForm, self).__init__(data=data, files=files, instance=instance, **kwargs)

    def save(self, commit=True):
        with transaction.atomic():
            return super(SocioeconomicNutritionExpertForm, self).save(commit)

    class Meta(ConsoleUserForm.Meta):
        model = SocioeconomicNutritionExpert
        fields = ['name', 'role']
