from blackwidow.core.forms.configurabletypes.configurabletype_form_mixin import ConfigurableTypeFormMixin
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.nuprp_admin.models import TradeSector

__author__ = 'Ziaul Haque'


class TradeSectorForm(ConfigurableTypeFormMixin):
    class Meta(GenericFormMixin.Meta):
        model = TradeSector
        fields = ['name']
