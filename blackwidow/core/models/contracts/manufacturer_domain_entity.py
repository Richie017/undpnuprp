from django.db import models
from modeltranslation.translator import TranslationOptions

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.manufacturers.manufacturer import Manufacturer

__author__ = 'Mahmud'


class ManufacturerDomainEntity(OrganizationDomainEntity):
    name = models.CharField(max_length=200)
    manufacturer = models.ForeignKey(Manufacturer, null=True)
    is_master = models.BooleanField(default=0)

    @classmethod
    def get_dependent_field_list(cls):
        return ['manufacturer']

    class Meta(OrganizationDomainEntity.Meta):
        abstract = True

    def load_initial_data(self, **kwargs):
        super().load_initial_data(**kwargs)

        manufacturer = Manufacturer.objects.first() if Manufacturer.objects.count() > 0 else Manufacturer()
        if manufacturer.pk is None:
            manufacturer.name = "Manufacturer " + str(kwargs['index'])
            manufacturer.organization = kwargs['org']
            manufacturer.save()
        self.manufacturer = manufacturer

    def save(self, *args, **kwargs):
        self.is_master = self.manufacturer.is_master if self.manufacturer is not None else False
        super().save(*args, **kwargs)

    @classmethod
    def get_translator_options(cls):
        class DETranslationOptions(TranslationOptions):
            fields = ('name', )
        return DETranslationOptions

    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()

        class ODESerializer(ss):

            class Meta:
                model = cls
                read_only_fields = ss.Meta.read_only_fields

        return ODESerializer
