from django import forms
from django.contrib.contenttypes.models import ContentType

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.roles.role_filter import RoleFilterEntity
from config.apps import INSTALLED_APPS

__author__ = 'Machine II'


class RoleFilterEntityForm(GenericFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        app_names = ContentType.objects.filter(app_label__in=INSTALLED_APPS).values('app_label').distinct()
        app_names = [(x['app_label'], x['app_label']) for x in app_names]
        model_names = ContentType.objects.filter(app_label__in=INSTALLED_APPS).values('model').order_by('model')
        model_names = [(x['model'], x['model']) for x in model_names]
        self.fields['target_model_app'] = forms.ChoiceField(label='Select App', choices=app_names,
                                                            widget=forms.Select(
                                                                attrs={'class': 'select2 app_label_select'}))
        self.fields['target_model'] = forms.ChoiceField(label='Select Model', choices=model_names,
                                                        widget=forms.Select(attrs={'class': 'select2 model_select'}))
        self.fields['query_str'].widget.attrs = {'class': 'model_field_text form-control', 'width': '520'}
        self.fields['value'].widget.attrs = {'class': 'value_field_text form-control', 'width': '520'}

    class Meta(GenericFormMixin.Meta):
        model = RoleFilterEntity
        fields = ['target_model_app', 'target_model', 'query_str', 'value']
