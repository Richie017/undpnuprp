from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.nuprp_admin.models.infrastructure_units.federation import Federation

__author__ = "Shama"


class FederationForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super().__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)

    class Meta(GenericFormMixin.Meta):
        model = Federation
        fields = 'name',
