from django.db import models
from rest_framework import serializers

from blackwidow.core.models.common.location import Location
from blackwidow.core.models.contracts.base import DomainEntity
from blackwidow.core.models.geography.geography import Geography
from blackwidow.engine.decorators.utility import loads_initial_data, decorate

__author__ = 'Mahmud'


@decorate(loads_initial_data)
class ContactAddress(DomainEntity):
    street = models.CharField(default='', max_length=500)
    city = models.CharField(default='', max_length=200)
    province = models.CharField(default='', max_length=200)
    geography = models.ForeignKey('core.Geography', null=True)
    postcode = models.CharField(default='', max_length=10)
    is_primary = models.BooleanField(default=0)
    location = models.ForeignKey(Location, null=True)
    address_type = models.CharField(max_length=200, default='Home Address')

    @classmethod
    def get_dependent_field_list(cls):
        return ['location']

    @property
    def region(self):
        return self.division_id if self.division_id is not None else 0

    @property
    def district(self):
        return self.state_id if self.state_id is not None else 0

    @property
    def township(self):
        return self.upazila_id if self.upazila_id is not None else 0

    @classmethod
    def get_serializer(cls):
        ss = DomainEntity.get_serializer()

        class ODESerializer(ss):
            geography = serializers.PrimaryKeyRelatedField(required=False, queryset=Geography.objects.all())
            city = serializers.CharField(required=False)
            province = serializers.CharField(required=False)
            street = serializers.CharField(required=False, allow_blank=True)
            address = serializers.SerializerMethodField()
            location = Location.get_serializer()()

            def get_address(self, obj):
                return obj.__str__()

            class Meta:
                model = cls
                read_only_fields = ss.Meta.read_only_fields + ('organization',)
                fields = ('id', 'code', 'geography', 'province', 'city', 'street', 'location', 'address')

        return ODESerializer

    def load_initial_data(self, **kwargs):
        super().load_initial_data(**kwargs)
        self.street = "Street Address " + str(kwargs['index'])
        self.city = "City " + str(kwargs['index'])

        # country = Country.objects.first() if Country.objects.count() > 0 else Country()
        # if country.pk is None:
        #     country.name = "Bangladesh"
        #     country.organization = kwargs['org']
        #     country.save()
        #
        # state = State.objects.filter(parent=country)[0] if State.objects.filter(parent=country).count() > 0 else State()
        # if state.pk is None:
        #     state.name = "Dhaka"
        #     state.organization = kwargs['org']
        #     state.parent = country
        #     state.save()
        #
        # self.country = country
        # self.state = state
        # self.save()

    def __str__(self):
        address = list()
        if self.street:
            address.append(self.street)
        if self.city:
            address.append(self.city)
        if self.province:
            address.append(self.province)
        geography = self.geography
        while geography is not None:
            address.append(geography.level.name + ': ' + geography.name)
            geography = geography.parent
        return ', '.join(address)
