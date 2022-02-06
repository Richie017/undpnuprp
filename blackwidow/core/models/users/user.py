from importlib._bootstrap_external import SourceFileLoader

from crequest.middleware import CrequestMiddleware
from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils.safestring import mark_safe
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from blackwidow.core.models.common.bank_info import BankAccountDetails, MobileBankingDetails
from blackwidow.core.models.common.contactaddress import ContactAddress
from blackwidow.core.models.common.custom_field import CustomFieldValue
from blackwidow.core.models.common.educational_qualification import EducationalQualification
from blackwidow.core.models.common.emailaddress import EmailAddress
from blackwidow.core.models.common.phonenumber import PhoneNumber
from blackwidow.core.models.common.qr_code import QRCode
from blackwidow.core.models.common.setting_item_value import SettingsItemValue
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.file.imagefileobject import ImageFileObject
from blackwidow.core.models.roles.role import Role
from blackwidow.core.models.structure.infrastructure_unit import InfrastructureUnit
from blackwidow.core.serializers.user_serializer import UserSerializer
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.decorators.enable_assignment import enable_assignment
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context, track_assignments
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.organizational_hierarchy_travarser import traverse_infrastructure_unit_hierarchy

__author__ = 'mahmudul, Tareq'

_CHOICES_MF = (
    ('M', 'Male'),
    ('F', 'Female'),
)


@decorate(is_object_context,
          route(route='users', group='Users', module=ModuleEnum.Settings,
                display_name='Other User', hide=True, group_order=1, item_order=100),
          enable_assignment(targets=['route'], role=['user']), track_assignments)
class ConsoleUser(OrganizationDomainEntity):
    user = models.OneToOneField(User, null=True)
    is_super = models.BooleanField(default=False)
    name = models.CharField(max_length=200)
    addresses = models.ManyToManyField(ContactAddress)
    emails = models.ManyToManyField(EmailAddress)
    phones = models.ManyToManyField(PhoneNumber)
    role = models.ForeignKey(Role, null=False)
    qr_code = models.ForeignKey(QRCode, null=True, on_delete=models.SET_NULL)
    male_or_female = models.CharField(max_length=2, choices=_CHOICES_MF, null=True, default='M')
    device_id = models.CharField(max_length=200, default=None, null=True)
    settings_value = models.ManyToManyField(SettingsItemValue)
    custom_fields = models.ManyToManyField(CustomFieldValue)
    bank_details = models.OneToOneField(BankAccountDetails, null=True)
    mobile_banking_details = models.OneToOneField(MobileBankingDetails, null=True)
    education = models.OneToOneField(EducationalQualification, null=True)
    image = models.ForeignKey(ImageFileObject, null=True, default=None)
    client = models.ForeignKey('core.Client', null=True, default=None, related_name='consoleuser_client',
                               on_delete=models.SET_NULL)
    assigned_to = models.ForeignKey(InfrastructureUnit, null=True, default=None, on_delete=models.SET_NULL)
    assigned_units = models.ManyToManyField(InfrastructureUnit, related_name="assigned_units")
    date_of_birth = models.CharField(max_length=200, default='')
    national_id = models.CharField(max_length=200, default='')
    is_alert_notified = models.BooleanField(default=False)
    assigned_code = models.CharField(max_length=128, blank=True, null=True)

    @property
    def details_config(self):
        d = super(ConsoleUser, self).details_config

        for x in self.custom_fields.all():
            d[x.field.name] = x.value

        index = 1
        for x in self.addresses.all():
            d['address ' + str(index)] = str(x)
            index += 1

        return d

    def details_link_config(self, **kwargs):
        consoleUserDetailLinkConfig = super(ConsoleUser, self).details_link_config(**kwargs)
        _request = CrequestMiddleware.get_request()
        consoleUserDetailLinkConfig.append(
            dict(
                name='Reset Password',
                title='Reset Password',
                action='print',
                icon='icon-key',
                ajax='0',
                url_name='consoleuser_reset_password'
            ),
        )

        return consoleUserDetailLinkConfig

    @property
    def tabs_config(self):
        tabs = [TabView(
            title='Settings',
            access_key='settings_value',
            route_name=self.__class__.get_route_name(action=ViewActionEnum.Tab),
            relation_type=ModelRelationType.INVERTED,
            related_model=SettingsItemValue,
            property=self.settings_value
        )]
        return tabs

    @classmethod
    def get_custom_serializers(cls):
        return ('user', UserSerializer),

    def to_business_user(self):
        for x in ConsoleUser.__subclasses__():
            if x.__name__ == self.type:
                self.__class__ = x
        return self

    def __init__(self, *args, **kwargs):
        super(ConsoleUser, self).__init__(*args, **kwargs)

    @classmethod
    def serialize_fields(self, prefix=''):
        return [
            {
                "controlType": "inputText",
                "textBoxType": "singline",
                "story": "Name",
                "textBoxInputType": "alphanumeric",
                "name": "name"
            }
        ]

    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()

        class Serializer(ss):

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if self.context['request'].method == 'GET':
                    self.fields['image'] = ImageFileObject.get_serializer()(required=False)

            role = serializers.PrimaryKeyRelatedField(required=True, queryset=Role.objects.all())
            addresses = ContactAddress.get_serializer()(many=True, required=False)
            emails = EmailAddress.get_serializer()(many=True, required=False)
            phones = PhoneNumber.get_serializer()(many=True, required=False)
            qr_code = QRCode.get_serializer()(many=False, required=False)
            device_id = serializers.CharField(max_length=200, required=False, default="")
            male_or_female = serializers.CharField(max_length=200, required=False, default="M")
            custom_fields = CustomFieldValue.get_serializer()(many=True, required=False)
            bank_details = BankAccountDetails.get_serializer()(required=False)
            mobile_banking_details = MobileBankingDetails.get_serializer()(required=False)
            education = EducationalQualification.get_serializer()(required=False)
            image = serializers.PrimaryKeyRelatedField(required=False, queryset=ImageFileObject.objects.all())
            user = UserSerializer(required=True)
            settings_value = serializers.PrimaryKeyRelatedField(required=False, many=True,
                                                                queryset=SettingsItemValue.objects.none())

            def validate_user(self, user):
                if user is not None:
                    if 'username' not in user:
                        return user
                    if self.instance and User.objects.filter(username__iexact=user['username']).exclude(
                            pk=self.instance.user.id).exists():
                        raise ValidationError('Username already exists.')
                return user

            def update(self, instance, validated_data):
                with transaction.atomic():
                    user = validated_data.pop('user', None)
                    # custom_fields = validated_data.pop('custom_fields', None)

                    instance = super(ConsoleUser, self).update(instance, validated_data)

                    if user is not None:
                        if 'username' in user.keys():
                            instance.user.username = user['username']
                        if 'password' in user.keys():
                            instance.user.set_password(user['password'])
                        instance.user.save()

                    # if custom_fields is not None:
                    # for f in custom_fields:
                    # field = self.custom_fields.filter(field__name=f['name'])
                    # if field.exists():
                    # field = field.first()
                    # CustomFieldValue.get_serializer()(self.context).update(field, f)

                    return instance

            def create(self, validated_data):
                with transaction.atomic():
                    instance = super(ConsoleUser, self).create(validated_data)
                    if instance.custom_fields.exists():
                        for x in instance.custom_fields.all():
                            if x.pk not in [instance.role.custom_fields.values_list('pk')]:
                                instance.role.custom_fields.add(x.field)
                    return instance

            class Meta(ss.Meta):
                model = cls
                fields = (
                    'id', 'name', 'role', 'addresses', 'emails', 'phones', 'qr_code', 'device_id', 'male_or_female',
                    'bank_details',
                    'custom_fields', 'mobile_banking_details', 'education', 'image', 'settings_value', 'user')

        return Serializer

    # def details_link_config(self, **kwargs):insta
    # return super().details_link_config(**kwargs)

    def to_json(self, depth=0, expand=None, wrappers=[], conditional_expand=[], include_m2m=False, **kwargs):
        obj = super(ConsoleUser, self).to_json(depth, expand, wrappers, conditional_expand, include_m2m=include_m2m,
                                               **kwargs)
        qr_code = None
        if self.qr_code:
            qr_code = self.qr_code.value
        obj['qr_code'] = qr_code
        obj['role_name'] = self.role.name
        return obj

    def save(self, *args, **kwargs):
        with transaction.atomic():
            created = False
            if self.pk is None:
                created = True
            if self.qr_code is not None:
                self.qr_code.is_used = True
                self.qr_code.save()
            super(ConsoleUser, self).save(*args, **kwargs)

    @classmethod
    def get_dependent_field_list(cls):
        return ['addresses', 'emails', 'phones', 'settings_value', 'user', 'custom_fields', 'bank_details', 'education']

    def get_choice_name(self):
        return self.name

    # def __str__(self):
    #     return self.code + ": " + self.name

    @property
    def render_phone(self):
        return ', '.join([str(x) for x in self.phones.all()])

    @property
    def render_address(self):
        return ', '.join([str(x) for x in self.addresses.all()])

    @property
    def assigned_to_infrastructure_unit(self):
        return self.assigned_to

    @property
    def render_assignment_hierarchy(self):
        h_list = traverse_infrastructure_unit_hierarchy([self.assigned_to_infrastructure_unit])
        h_str = ''
        for infrastructure in h_list:
            h_str = infrastructure.__str__() + (' > ' if h_str else '') + h_str
        return mark_safe(h_str)

    @classmethod
    def table_columns(cls):
        return "render_code", "name", "render_address", "render_phone", "last_updated"

    def filter_model(self, queryset=None, **kwargs):
        app_label = self.app_full_label(dir_format=True)
        try:
            q_filter = SourceFileLoader('app_label',
                                        app_label + '/models/users/filters/' + self.type.lower() + '_filter.py') \
                .load_module().get_filter_for_model(self, queryset.model)
            if q_filter:
                return queryset.filter(q_filter)
            return queryset
        except Exception as exp:
            return queryset

    def delete(self, *args, **kwargs):
        if self.qr_code:
            self.qr_code.is_used = False
            self.qr_code.save()

        # delete the django user
        self.user.delete()

        super(ConsoleUser, self).delete(*args, **kwargs)
