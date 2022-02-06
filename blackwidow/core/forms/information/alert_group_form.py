from django import forms

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.information.alert_group import AlertGroup

__author__ = 'ruddra'


class AlertGroupForm(GenericFormMixin):
    class Meta(GenericFormMixin.Meta):
        model = AlertGroup
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(),
            }