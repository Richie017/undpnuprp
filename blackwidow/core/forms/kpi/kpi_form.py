import datetime

from django import forms
from django.core.urlresolvers import reverse

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.contracts.kpi_base import PerformanceIndex
from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.clock import Clock

__author__ = 'activehigh'


class PerformanceIndexForm(GenericFormMixin):
    start_time = forms.CharField(required=False, max_length=20, widget=forms.TextInput(
        attrs={'class': 'date-time-picker', 'data-format': "dd/MM/yyyy"}))
    end_time = forms.CharField(required=False, max_length=20,
                               widget=forms.TextInput(attrs={'class': 'date-time-picker', 'data-format': "dd/MM/yyyy"}))

    def __init__(self, instance=None, **kwargs):
        super().__init__(instance=instance, **kwargs)
        self.fields['user'] = GenericModelChoiceField(queryset=ConsoleUser.objects.all(), widget=forms.TextInput(
            attrs={'class': 'select2-input', 'data-url': reverse(
                ConsoleUser.get_route_name(action=ViewActionEnum.Manage)) + "?search=1&format=json"}))

    def clean_start_time(self):
        if 'start_time' not in self.cleaned_data:
            return 0
        _date = datetime.datetime.strptime(self.cleaned_data['start_time'], "%d/%m/%Y")
        _value = Clock.get_user_universal_time(_date.timestamp())
        return _value.timestamp() * 1000

    def clean_end_time(self):
        if 'end_time' not in self.cleaned_data:
            return 0
        _date = datetime.datetime.strptime(self.cleaned_data['end_time'], "%d/%m/%Y")
        return Clock.get_user_universal_time(_date.timestamp()).timestamp() * 1000

    def clean_user(self):
        return self.cleaned_data['user']

    def clean(self):
        return super().clean()

    class Meta:
        model = PerformanceIndex
        fields = ['name', 'user', 'start_time', 'end_time', 'target', 'achieved']
        labels = {
            'start_time': 'from',
            'end_time': 'to'
        }
