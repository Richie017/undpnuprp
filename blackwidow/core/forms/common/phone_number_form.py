from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.common.phonenumber import PhoneNumber

__author__ = 'ruddra'

from django import forms


class PhoneNumberForm(GenericFormMixin):
    phone = forms.CharField(max_length=100, required=False)
    owner = forms.CharField(label='Phone Owner', widget=forms.Select(attrs={'class': 'select2'}, choices=PhoneNumber.get_owner_choices()))
    class Meta(GenericFormMixin.Meta):
        model = PhoneNumber
        fields = ['phone', 'owner']
