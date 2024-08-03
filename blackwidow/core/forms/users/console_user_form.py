from django import forms
from django.db import transaction
from django.forms.models import modelformset_factory

from blackwidow.core.forms import EmailAddressForm
from blackwidow.core.forms.common.contact_address_form import ContactAddressForm
from blackwidow.core.forms.common.phone_number_form import PhoneNumberForm
from blackwidow.core.forms.files.imagefileobject_form import ImageFileObjectForm
from blackwidow.core.forms.users.account_inline_form import AccountInlineForm
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin, GenericModelFormSetMixin
from blackwidow.core.models import EmailAddress
from blackwidow.core.models.common.contactaddress import ContactAddress
from blackwidow.core.models.common.custom_field import CustomFieldValue
from blackwidow.core.models.common.phonenumber import PhoneNumber
from blackwidow.core.models.roles.role import Role
from blackwidow.core.models.users.settings.user_settings import TimeZoneSettingsItem
from blackwidow.core.models.users.user import ConsoleUser, SettingsItemValue
from blackwidow.engine.decorators.utility import get_models_with_decorator
from blackwidow.engine.extensions import bw_titleize
from blackwidow.engine.extensions.generate_form_fields import genarate_form_field
from blackwidow.engine.extensions.list_extensions import inserted_list
from config.apps import INSTALLED_APPS
from settings import TIME_ZONE_DEFAULT_OFFSET

__author__ = 'Tareq'

contact_address_formset = modelformset_factory(ContactAddress, form=ContactAddressForm,
                                               formset=GenericModelFormSetMixin, extra=0, min_num=1, validate_min=True,
                                               can_delete=True)
phone_number_formset = modelformset_factory(PhoneNumber, form=PhoneNumberForm, formset=GenericModelFormSetMixin,
                                            extra=0, min_num=1, validate_min=True, can_delete=True)
email_formset = modelformset_factory(EmailAddress, form=EmailAddressForm, formset=GenericModelFormSetMixin, extra=0,
                                     min_num=1, validate_min=True, can_delete=True)


def get_role_for_model(model_class):
    model_name = model_class.__name__
    is_role_context_found = False
    role_class = None
    while model_name != 'DomainEntity':
        decorators = [x.__name__ for x in model_class._decorators]
        if 'is_role_context' in decorators:
            is_role_context_found = True
            role_class = model_class
            break
        else:
            model_class = model_class.__base__
            model_name = model_class.__name__
    return is_role_context_found, role_class


class ConsoleUserForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, allow_login=True, **kwargs):
        super().__init__(data=data, files=files, instance=instance, **kwargs)
        if self.fields['role'].initial is None:
            self.fields['role'].initial = ('', '-')

        if not self.request.c_user.is_super:
            if 'is_super' in self.fields:
                self.fields['is_super'].widget = forms.HiddenInput()
                self.fields['is_super'].initial = False

        # check if role context or not
        model_class = self.Meta.model

        is_role_context_found, role_class = get_role_for_model(model_class)

        _role_name = role_class.get_model_meta('route', 'display_name') or role_class.__name__

        roles = Role.objects.filter(name=_role_name)
        if is_role_context_found:
            self.fields['role'].choices = [(x.id, x.name) for x in roles]
        else:
            roles = Role.objects.all()
            business_roles = get_models_with_decorator('is_business_role', INSTALLED_APPS)
            self.fields['role'].choices = inserted_list(
                [(x.id, x.name) for x in Role.objects.all() if x.name not in business_roles], 0, ('', ' --'))

        if allow_login and instance is None:
            kwargs.update({
                'prefix': 'account'
            })
            self.add_child_form("user", AccountInlineForm(data, files, form_header='Login Information',
                                                          instance=instance.user if instance else None, **kwargs),
                                is_prefix_form=True)

        if self.instance is not None and self.instance.pk is not None:
            addresses = self.instance.addresses.all()
            phones = self.instance.phones.all()
            emails = self.instance.emails.all()
            custom_fields = self.instance.custom_fields.all()
        else:
            addresses = ContactAddress.objects.none()
            phones = PhoneNumber.objects.none()
            emails = EmailAddress.objects.none()
            custom_fields = CustomFieldValue.objects.none()
        kwargs.update({
            'prefix': 'address'
        })
        self.add_child_form("addresses",
                            contact_address_formset(data=data, files=files, queryset=addresses, header='Address',
                                                    add_more=True, **kwargs))
        kwargs.update({
            'prefix': 'phone'
        })
        self.add_child_form("phones", phone_number_formset(data=data, files=files, queryset=phones, header='Phone',
                                                           add_more=False, **kwargs))
        kwargs.update({
            'prefix': 'email'
        })
        self.add_child_form("emails",
                            email_formset(data=data, files=files, queryset=emails, header='Email', add_more=False,
                                          **kwargs))
        kwargs.update({
            'prefix': 'image'
        })
        self.add_child_form("image", ImageFileObjectForm(data=data, files=files,
                                                         instance=instance.image if instance is not None else None,
                                                         form_header='Profile Picture', **kwargs))

        model_class = self.Meta.model

        is_role_context_found, role_class = get_role_for_model(model_class)

        if len(roles) > 0 and is_role_context_found:
            kwargs.update({
                'prefix': 'meta'
            })
            custom_field_form = self
            _index = 0
            custom_fiels = roles[0].custom_fields.all().order_by('name')
            for x in custom_fiels:
                field_instance_args = {
                    'label': bw_titleize(x.name),
                    'required': x.is_required,
                }
                custom_field_form.fields['field_' + str(_index)] = genarate_form_field(x, field_instance_args)
                if x.name not in [f.field.name for f in custom_fields]:
                    custom_field_form.fields['field_' + str(_index)].initial = ""
                else:
                    custom_field_form.fields['field_' + str(_index)].initial = \
                        [f.value for f in custom_fields if f.field.name == x.name][0]
                _index += 1

    def validate_unique(self):
        super().validate_unique()

    def save(self, commit=True):
        with transaction.atomic():
            self.instance = super().save(commit)

            is_role_context_found, role_class = get_role_for_model(self.Meta.model)

            _role_name = role_class.get_model_meta('route', 'display_name') or role_class.__name__
            roles = Role.objects.filter(name=_role_name)
            self.instance.custom_fields.clear()
            if len(roles) > 0 and is_role_context_found:
                custom_field_form = self
                index = 0
                for x in roles[0].custom_fields.all().order_by('name'):
                    if ('field_' + str(index)) in custom_field_form.fields:
                        value = custom_field_form.cleaned_data['field_' + str(index)]
                    else:
                        value = ""
                    f_value = CustomFieldValue()
                    f_value.organization = self.instance.organization
                    f_value.value = value
                    f_value.field = x
                    f_value.save()
                    self.instance.custom_fields.add(f_value)
                    index += 1

            # tz_settings, result = TimeZoneSettingsItem.objects.get_or_create(organization=self.request.c_organization)
            # if result:
            #     tz_settings.save()
            # tz_value, result = SettingsItemValue.objects.get_or_create(organization=self.request.c_organization,
            #                                                            consoleuser__id=self.instance.pk,
            #                                                            settings_item=tz_settings)
            # if result:
            #     tz_value.value = str(-360)
            #     tz_value.save()
            tz_offset = TIME_ZONE_DEFAULT_OFFSET
            TimeZoneSettingsItem.cache_user_timezone_offset(user_id=self.instance.pk, offset_value=tz_offset)
            return self.instance

    class Meta(GenericFormMixin.Meta):
        model = ConsoleUser
        fields = ['name', 'role', 'is_super']
        labels = {
            'name': 'Full Name',
            'male_or_female': 'Male or female?'
        }
        widgets = {
            'role': forms.Select(attrs={'class': 'select2'}),
            'organization': forms.HiddenInput(attrs={'class': 'select2'})
        }
