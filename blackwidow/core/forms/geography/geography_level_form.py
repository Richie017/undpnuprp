from django import forms

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.geography.geography_level import GeographyLevel

__author__ = 'Tareq'


class GeographyLevelForm(GenericFormMixin):
    def __init__(self, data=None, files=None, prefix=None, instance=None, **kwargs):
        super(GeographyLevelForm, self).__init__(data=data, files=files, prefix=prefix, instance=instance, **kwargs)
        self.fields['parent'] = GenericModelChoiceField(queryset=GeographyLevel.objects.all(), empty_label='Select One',
                                                        required=False,
                                                        widget=forms.Select(attrs={'class': 'select2', 'width': '220'}),
                                                        initial=self.instance.parent if self.instance.pk else None)


    class Meta(GenericFormMixin.Meta):
        model = GeographyLevel
        fields = 'name', 'parent',
