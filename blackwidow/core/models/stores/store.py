from django.db import models
from django.db.models.deletion import SET_NULL
from rest_framework import serializers

from blackwidow.core.models.common.contactaddress import ContactAddress
from blackwidow.core.models.common.emailaddress import EmailAddress
from blackwidow.core.models.common.phonenumber import PhoneNumber
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.users.web_user import WebUser

__author__ = 'Mahmud'


class Store(OrganizationDomainEntity):
    name = models.CharField(max_length=500, default='')
    contact_person = models.ForeignKey(WebUser, null=True, on_delete=SET_NULL)
    address = models.ForeignKey(ContactAddress, null=True, on_delete=SET_NULL)
    email = models.ForeignKey(EmailAddress, null=True, on_delete=SET_NULL)
    phone_number = models.ForeignKey(PhoneNumber, null=True, on_delete=SET_NULL)

    @classmethod
    def get_dependent_field_list(cls):
        return ['address', 'location', 'email', 'phone_number']

    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()

        class Serializer(ss):
            name = serializers.CharField(max_length=200)
            address = ContactAddress.get_serializer()(required=True)
            contact_person = WebUser.get_serializer()(required=False)
            email = EmailAddress.get_serializer()(required=False)
            phone_number = PhoneNumber.get_serializer()(required=False)

            class Meta(ss.Meta):
                model = cls
                depth = 1

        return Serializer
