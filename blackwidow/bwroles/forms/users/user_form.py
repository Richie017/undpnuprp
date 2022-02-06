from django import forms
from django.db import transaction

from blackwidow.core.forms.files.imagefileobject_form import ImageFileObjectForm
from blackwidow.core.forms.users.account_inline_form import AccountInlineForm
from blackwidow.core.forms.users.console_user_form import phone_number_formset
from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.common.phonenumber import PhoneNumber
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.core.models.roles.role import Role
from blackwidow.core.models.users.user import ConsoleUser

__author__ = 'Sohel'


class GenericUserForm(GenericFormMixin):
    def get_role_object_for_model(self):
        # check if role context or not
        model_class = self.Meta.model
        _role_name = model_class.get_model_meta('route', 'display_name') or model_class.__name__
        all_role_models = Role.objects.filter(name__iexact=_role_name)

        return all_role_models

    def __init__(self, data=None, files=None, instance=None, allow_login=True, **kwargs):
        super().__init__(data=data, files=files, instance=instance, **kwargs)

        user_roles = self.get_role_object_for_model()

        self.fields['role'].choices = [(x.id, x.name) for x in user_roles]
        self.fields['organization'] = GenericModelChoiceField(
            required=True, queryset=Organization.objects.filter(is_deleted=False),
            widget=forms.Select(attrs={'class': 'select2'}),
            initial=instance.organization if instance is not None else None)

        if allow_login and instance is None:
            kwargs.update({
                'prefix': 'account'
            })
            self.add_child_form("user", AccountInlineForm(data, files, form_header='Login Information',
                                                          instance=instance.user if instance else None, **kwargs),
                                is_prefix_form=True)

        if self.instance is not None and self.instance.pk is not None:
            # addresses = self.instance.addresses.all()
            phones = self.instance.phones.all()
        else:
            # addresses = ContactAddress.objects.none()
            phones = PhoneNumber.objects.none()
        kwargs.update({
            'prefix': 'address'
        })
        # self.add_child_form("addresses",
        #                     contact_address_formset(data=data, files=files, queryset=addresses, header='Address',
        #                                             add_more=True, **kwargs))
        kwargs.update({
            'prefix': 'phone'
        })
        self.add_child_form("phones", phone_number_formset(data=data, files=files, queryset=phones, header='Phone',
                                                           add_more=False, **kwargs))
        kwargs.update({
            'prefix': 'email'
        })
        kwargs.update({
            'prefix': 'image'
        })
        self.add_child_form("image", ImageFileObjectForm(data=data, files=files,
                                                         instance=instance.image if instance is not None else None,
                                                         form_header='Profile Picture', **kwargs))

    def validate_unique(self):
        super().validate_unique()

    def save(self, commit=True):
        with transaction.atomic():
            # self.instance.organization = self.cleaned_data['organization']
            self.instance = super(GenericUserForm, self).save(commit)
            return self.instance

    class Meta(GenericFormMixin.Meta):
        model = ConsoleUser
        fields = ['name', 'role', 'organization']
        labels = {
            'name': 'Full Name'
        }
        widgets = {
            'role': forms.Select(attrs={'class': 'select2'}),
        }
