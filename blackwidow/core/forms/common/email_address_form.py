from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.common.emailaddress import EmailAddress

__author__ = 'ruddra'

from django import forms


class EmailAddressForm(GenericFormMixin):
    email = forms.EmailField(label="Email")
    is_primary = forms.BooleanField(label="Is primary address?", required=False, initial=True, widget=forms.HiddenInput)

    class Meta(GenericFormMixin.Meta):
        model = EmailAddress
        fields = ['email', 'is_primary']
