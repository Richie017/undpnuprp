from django.db import models

from blackwidow.core.models.common.contactaddress import ContactAddress
from blackwidow.core.models.common.emailaddress import EmailAddress
from blackwidow.core.models.common.phonenumber import PhoneNumber
from blackwidow.core.models.contracts.base import DomainEntity

__author__ = 'Tareq'


class WebUser(DomainEntity):
    name = models.CharField(max_length=200)
    address = models.ForeignKey(ContactAddress, null=True, on_delete=models.SET_NULL)
    email = models.ForeignKey(EmailAddress, null=True, on_delete=models.SET_NULL)
    phone = models.ForeignKey(PhoneNumber, null=True, on_delete=models.SET_NULL)
    designation = models.CharField(max_length=200, default='')

    @classmethod
    def get_serializer(cls):
        ss = DomainEntity.get_serializer()

        class Serializer(ss):
            address = ContactAddress.get_serializer()(required=False)
            email = EmailAddress.get_serializer()(required=False)
            phone = PhoneNumber.get_serializer()(required=False)

            class Meta(ss.Meta):
                model = cls

        return Serializer

    @classmethod
    def get_dependent_field_list(cls):
        return ['address', 'email', 'phone']

    def load_initial_data(self, **kwargs):
        super().load_initial_data(**kwargs)
        self.name = "Web user " + str(kwargs['index'])

        address = ContactAddress()
        address.load_initial_data(**kwargs)
        self.address = address

        email = EmailAddress()
        email.load_initial_data(**kwargs)
        self.email = email
        self.save()

    def __str__(self):
        result = self.name
        result += ",<br/><em>address: </em>" + str(self.address)
        result += ',<br/><em>email: </em>' + str(self.email)
        return result
