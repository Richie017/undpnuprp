from collections import OrderedDict

from blackwidow.core.forms.configurabletypes.configurabletype_form_mixin import ConfigurableTypeFormMixin
from undp_nuprp.nuprp_admin.models.descriptors.training_participant import TrainingParticipant


class TrainingParticipantForm(ConfigurableTypeFormMixin):
    class Meta:
        model = TrainingParticipant
        fields = ['name']
