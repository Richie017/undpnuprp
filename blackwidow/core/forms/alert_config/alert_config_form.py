from blackwidow.core.mixins.fieldmixin.multiple_select_field_mixin import GenericModelMultipleChoiceField
from blackwidow.core.models.alert_config.alert_config import AlertConfig, AlertActionEnum, Operator
from blackwidow.core.models.roles.role import Role
from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.engine.decorators.utility import get_models_with_decorator
from blackwidow.engine.extensions.bw_titleize import bw_titleize
from blackwidow.engine.extensions.model_descriptor import get_model_description
from settings import INSTALLED_APPS

__author__ = 'ruddra'
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from django import forms


class AlertConfigForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', parent_id='', **kwargs):
        super().__init__(data=data, files=files, instance=instance, prefix=prefix, parent_id=parent_id, **kwargs)
        # _role_url = reverse(Role.get_route_name(action=ViewActionEnum.Manage))
        # self.fields['recipient_roles'] = GenericModelMultipleChoiceField(required=False, queryset=Role.objects.all(), widget=forms.TextInput(attrs={'class': 'select2-input', 'multiple': 'multiple', 'data-url': _role_url + "?format=json"}), initial=instance.recipient_roles.all() if instance is not None else None)
        # _user_url = reverse(ConsoleUser.get_route_name(action=ViewActionEnum.Manage))
        # self.fields['recipient_users'] = GenericModelMultipleChoiceField(required=False, queryset=ConsoleUser.objects.all(), widget=forms.TextInput(attrs={'class': 'select2-input', 'multiple': 'multiple', 'data-url': _user_url + "?format=json"}), initial=instance.recipient_users.all() if instance is not None else None)
        self.fields['recipient_roles'] = GenericModelMultipleChoiceField(required=False, queryset=Role.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'select2'}), initial=instance.recipient_roles.all() if instance is not None else None)
        self.fields['recipient_users'] = GenericModelMultipleChoiceField(required=False, queryset=ConsoleUser.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'select2'}), initial=instance.recipient_users.all() if instance is not None else None)
        models_with_trigger = get_models_with_decorator('enable_trigger', INSTALLED_APPS)
        choice_list = list()
        choice_list.append(('None', 'None'))
        for items in models_with_trigger:
            choice_list.append((items, bw_titleize(items)))
        self.fields['model'].widget.choices = choice_list
        self.fields['action'].widget.choices = AlertActionEnum.get_enum_list()
        self.fields['operation'].widget.choices = Operator.get_name(value=None)
        if not instance:
            self.fields['model_property'].widget.choices = [('None', 'None')]
        else:
            self.fields['model_property'].widget.choices = [(x, x) for x in get_model_description(model_name=instance.model)]+[('None', 'None')]
        
        
    class Meta(GenericFormMixin.Meta):
        model = AlertConfig
        fields = ['subject', 'body', 'model', 'action', 'operation', 'model_property',
                  'recipient_users', 'reference_value', 'sends_email']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'richtexteditor'}),
            'group': forms.Select(attrs={'class': 'select2'}),
            "action": forms.Select(attrs={'class': 'select2'}),
            "operation": forms.Select(attrs={'class': 'select2'}),
            "email_template": forms.Select(attrs={'class': 'select2'}),
            "model": forms.Select(attrs={'class': 'model-descriptor select'}),
            "model_property": forms.Select(attrs={'class': 'select model-property'}),
        }
