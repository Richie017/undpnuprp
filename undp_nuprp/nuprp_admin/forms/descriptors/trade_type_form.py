from django import forms

from blackwidow.core.forms.configurabletypes.configurabletype_form_mixin import ConfigurableTypeFormMixin
from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.nuprp_admin.models import TradeSector, TradeType

__author__ = 'Ziaul Haque'


class TradeTypeForm(ConfigurableTypeFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(TradeTypeForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['parent'] = \
            GenericModelChoiceField(
                queryset=TradeSector.objects.all(),
                label='Sector',
                widget=forms.Select(
                    attrs={
                        'class': 'select2',
                        'width': '220',
                    }
                )
            )

    class Meta(GenericFormMixin.Meta):
        model = TradeType
        fields = ['name', 'parent']
