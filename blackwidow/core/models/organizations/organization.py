from blackwidow.core.models.contracts.base import DomainEntity
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.constants.cache_constants import ORGANIZATION_CACHE, ONE_MONTH_TIMEOUT, SITE_NAME_AS_KEY
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.managers.cachemanager import CacheManager

__author__ = 'mahmudul'

from django.db import models

SUPER_ORGANIZATION_CACHE_KEY = SITE_NAME_AS_KEY + '_super_org'


# @decorate(save_audit_log, route(route='organizations', group='Organizations', module=ModuleEnum.Administration, display_name='Organization'))
class Organization(DomainEntity):
    name = models.CharField(max_length=255, unique=False)

    is_master = models.BooleanField(default=0)
    is_test = models.BooleanField(default=0)

    addresses = models.ManyToManyField('core.ContactAddress', related_name="addresses")
    emails = models.ManyToManyField('core.EmailAddress', related_name="emails")
    phones = models.ManyToManyField('core.PhoneNumber', related_name="phones")

    trade_license_number = models.CharField(max_length=200, default='')
    registration_date = models.BigIntegerField(null=True)
    date_joined = models.BigIntegerField(null=True)

    # @property
    # def details_config(self):
    #     data = super().details_config
    #     data['email'] = self.emails.first()
    #     data['phone'] = self.phones.first()
    #     data['address'] = self.addresses.first()
    #     return data
    @classmethod
    def get_datetime_fields(cls):
        return ['date_created', 'last_updated', 'date_joined', 'registration_date']

    @classmethod
    def get_organization_from_cache(cls):
        cache_key = ORGANIZATION_CACHE
        organization = CacheManager.get_from_cache_by_key(key=cache_key)
        if organization is None:
            organization = Organization.objects.first()
            CacheManager.set_cache_element_by_key(key=cache_key, value=organization, timeout=ONE_MONTH_TIMEOUT)
        return organization

    @classmethod
    def get_super_organization(cls):
        """
        Returns Field Buzz organization
        :return:         Returns Field Buzz organization
        """
        super_organization = CacheManager.get_from_cache_by_key(key=SUPER_ORGANIZATION_CACHE_KEY)
        if super_organization is None:
            _org = Organization.all_objects.filter(is_master=True).order_by('pk').first()
            super_organization = {
                'id': _org.pk, 'name': _org.name
            }
            CacheManager.set_cache_element_by_key(
                key=SUPER_ORGANIZATION_CACHE_KEY, value=super_organization, timeout=ONE_MONTH_TIMEOUT)
        return super_organization

    @classmethod
    def get_serializer(cls):
        ss = DomainEntity.get_serializer()

        class Serializer(ss):
            class Meta(ss.Meta):
                model = cls
                fields = ('id', 'code', 'name', 'is_master', 'addresses', 'emails', 'phones', 'trade_license_number',
                          'registration_date', 'date_joined')

        return Serializer

    def to_json(self, depth=0, expand=None, wrappers=[], conditional_expand=[], **kwargs):
        obj = dict()
        fields = ['id', 'name', 'code']
        for f in fields:
            if hasattr(self, f):
                obj[f] = getattr(self, f)
        return obj

    @classmethod
    def get_dependent_field_list(cls):
        return ['addresses', 'emails', 'phones']

    def get_choice_name(self):
        return self.name

    @property
    def tabs_config(self):
        from blackwidow.core.models.common.contactaddress import ContactAddress
        from blackwidow.core.models.common.emailaddress import EmailAddress
        from blackwidow.core.models.common.phonenumber import PhoneNumber

        tabs = [TabView(
            title='Addresses',
            access_key='addresses',
            route_name=self.__class__.get_route_name(action=ViewActionEnum.Tab),
            relation_type=ModelRelationType.NORMAL,
            related_model=ContactAddress,
            property=self.addresses
        ), TabView(
            title='Emails',
            access_key='emails',
            route_name=self.__class__.get_route_name(action=ViewActionEnum.Tab),
            relation_type=ModelRelationType.NORMAL,
            related_model=EmailAddress,
            property=self.emails
        ), TabView(
            title='Phones',
            access_key='phones',
            route_name=self.__class__.get_route_name(action=ViewActionEnum.Tab),
            relation_type=ModelRelationType.NORMAL,
            related_model=PhoneNumber,
            property=self.phones
        )]
        return tabs

    class Meta:
        app_label = 'core'
