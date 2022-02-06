from django import forms
from django.core.urlresolvers import reverse
from django.db import transaction

from blackwidow.core.mixins.fieldmixin.multiple_select_field_mixin import GenericModelMultipleChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.information.information_object import InformationObject
from blackwidow.core.models.roles.role import Role
from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.engine.enums.information_object_enum import InformationNotificationEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.exceptions.exceptions import BWException
from blackwidow.engine.extensions.clock import Clock

__author__ = 'Tareq'


class InformationObjectForm(GenericFormMixin):
    start_time_date = forms.DateTimeField()
    end_time_date = forms.DateTimeField()
    user_list = forms.CharField()

    def clean(self):
        if self.cleaned_data['start_time_date'] >= self.cleaned_data['end_time_date']:
            raise BWException("End time must be greater than start time.")
        return super().clean()

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, instance=None, **kwargs):
        super().__init__(data=data, files=files, auto_id=auto_id, prefix=prefix, instance=instance, **kwargs)
        self.fields['recipient_roles'] = GenericModelMultipleChoiceField(required=False, queryset=Role.objects.all(),
                                                                         widget=forms.SelectMultiple(
                                                                             attrs={'class': 'select2'}),
                                                                         initial=instance.recipient_roles.all() if instance is not None else None)
        self.fields['user_list'] = forms.CharField(
            label='Recipient users', required=False, widget=forms.TextInput(
                attrs={'class': 'select2-input', 'width': '220', 'multiple': 'multiple',
                       'data-depends-on': 'recipient_roles', 'data-depends-property': 'role:id', 'data-url': reverse(
                        ConsoleUser.get_route_name(
                            ViewActionEnum.Manage)) + '?search=1&format=json&disable_pagination=1'}
            ),
            initial=','.join([str(_id) for _id in instance.recipient_users.all()
                             .values_list('pk', flat=True)]) if instance is not None else None)

        self.fields['start_time_date'] = forms.DateTimeField(
            label='Start Time', input_formats=['%d/%m/%Y'], widget=forms.DateTimeInput(
                attrs={'data-format': "dd/MM/yyyy", 'class': 'date-time-picker', 'readonly': 'True'},
                format='%d/%m/%Y'), initial=Clock.get_user_local_time(instance.start_time) if instance else None)
        self.fields['end_time_date'] = forms.DateTimeField(
            label='End Time', input_formats=['%d/%m/%Y'], widget=forms.DateTimeInput(
                attrs={'data-format': "dd/MM/yyyy", 'class': 'date-time-picker', 'readonly': 'True'},
                format='%d/%m/%Y'), initial=Clock.get_user_local_time(instance.end_time) if instance else None)

        self.fields['notification_medium'] = forms.IntegerField(
            widget=forms.Select(attrs={'class': 'select2'}, choices=InformationNotificationEnum.get_choices()))

    def save(self, commit=True):
        with transaction.atomic():
            self.instance.start_time = (self.cleaned_data['start_time_date']).timestamp() * 1000
            self.instance.end_time = (self.cleaned_data['end_time_date'].replace(hour=23, minute=59,
                                                                                 second=59)).timestamp() * 1000
            self.instance = super().save(commit=False)
            self.instance.save()
            for item in self.cleaned_data['recipient_roles']:
                self.instance.recipient_roles.add(item)
            if self.cleaned_data['user_list']:
                self.instance.recipient_users.clear()
                user_pk_list = self.cleaned_data['user_list'].split(',')
                self.instance.recipient_users.add(*list(ConsoleUser.objects.filter(pk__in=user_pk_list)))
            return self.instance

    class Meta:
        model = InformationObject
        fields = ['name', 'details', 'recipient_roles', 'user_list', 'start_time_date',
                  'end_time_date', 'notification_medium']
        labels = {
            'name': 'Title',
            'details': 'Message'
        }
        widgets = {
            'details': forms.Textarea(attrs={'class': 'description'}),
        }
