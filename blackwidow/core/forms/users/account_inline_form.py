from django import forms
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.authtoken.models import Token

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin

__author__ = 'Tareq'


class AccountInlineForm(GenericFormMixin):
    username = forms.CharField(label="Login", max_length=200)
    password = forms.CharField(label="Password", widget=forms.PasswordInput())
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput())

    def __init__(self, data=None, files=None, instance=None, **kwargs):
        super().__init__(data=data, files=files, instance=instance, **kwargs)
        if instance:
            self.fields['username'].widget.attrs['readonly'] = True
            self.fields['password'].widget.attrs['readonly'] = True
            self.fields['confirm_password'].widget.attrs['readonly'] = True

    def clean(self):
        if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
            self.add_error('confirm_password', 'Password & Confirm Password must match.')
        return super().clean()

    def save(self, commit=True):
        with transaction.atomic():
            self.instance.save()
            self.instance.set_password(self.instance.password)
            self.instance = super().save(commit)
            Token.objects.get_or_create(user=self.instance)
            return self.instance

    def validate_unique(self):
        super().validate_unique()
        users = User.objects.filter(username__iexact=self.cleaned_data['username'])
        if len(users) > 0:
            self.add_error('username', 'User with id \'' + self.cleaned_data['username'] +
                           '\' already exists. Please choose a different login id.')

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password']
        widgets = {
            'password': forms.PasswordInput(),
            'confirm_password': forms.PasswordInput(),
        }
