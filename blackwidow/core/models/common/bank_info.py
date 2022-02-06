from django.utils.safestring import mark_safe

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.file.imagefileobject import ImageFileObject


__author__ = 'Mahmud'

from django.db import models


class BankAccountDetails(OrganizationDomainEntity):
    bank_name = models.CharField(max_length=200, default="")
    branch_name = models.CharField(max_length=200, default="")
    routing_number = models.CharField(max_length=200, default="")
    account_name = models.CharField(max_length=200, default="")
    account_number = models.CharField(max_length=200, default="")
    image_of_bank_cheque = models.ForeignKey(ImageFileObject, null=True)

    def __str__(self):
        return mark_safe("<strong>Bank Name: </strong>" + self.bank_name + '<br/>'
                         + "<strong>Branch Name: </strong>" + self.branch_name + '<br/>'
                         + "<strong>Routing Number: </strong>" + self.routing_number + '<br/>'
                         + "<strong>Account Name: </strong>" + self.account_name + '<br/>'
                         + "<strong>Account Number: </strong>" + self.account_number + '<br/>'
                         + "<strong>Image of Bank Cheque: </strong>" + str(self.image_of_bank_cheque))

    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()

        class Serializer(ss):
            image_of_bank_cheque = ImageFileObject.get_serializer()
            class Meta(OrganizationDomainEntity.Meta):
                model = cls
                fields = ( 'id', 'code', 'bank_name', 'branch_name', 'routing_number', 'account_name', 'account_number', 'image_of_bank_cheque' 'date_created' )
        return Serializer


class MobileBankingDetails(OrganizationDomainEntity):
    service_provider = models.CharField(max_length=200, default="")
    account_name = models.CharField(max_length=200, default="")
    mobile_number = models.CharField(max_length=200, default="")

    def __str__(self):
        return mark_safe("<strong>Service Provider: </strong>" + self.service_provider + '<br/>'
                         + "<strong>Account Name: </strong>" + self.account_name + '<br/>'
                         + "<strong>Mobile Number: </strong>" + self.mobile_number)

    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()

        class Serializer(ss):
            class Meta(OrganizationDomainEntity.Meta):
                model = cls
                fields = ( 'id', 'code', 'service_provider', 'account_name', 'mobile_number', 'date_created' )
        return Serializer



