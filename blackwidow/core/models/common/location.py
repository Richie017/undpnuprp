from decimal import Decimal

from django.db import models
from django.utils.safestring import mark_safe
from rest_framework.fields import empty

from blackwidow.core.models.contracts.base import DomainEntity


class Location(DomainEntity):
    latitude = models.DecimalField(max_digits=16, decimal_places=6, default=Decimal("000.00"), null=True)
    longitude = models.DecimalField(max_digits=16, decimal_places=6, default=Decimal("000.00"), null=True)
    accuracy = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), null=True)

    def load_initial_data(self, **kwargs):
        super(Location, self).load_initial_data(**kwargs)
        self.latitude = 23
        self.longitude = 90
        self.accuracy = ''

    @classmethod
    def get_serializer(cls):
        ss = DomainEntity.get_serializer()

        class ODESerializer(ss):

            def run_validation(self, data=empty):
                if data != empty:
                    try:
                        if 'accuracy' in data.keys():
                            if len(data['accuracy']) > 7:
                                data['accuracy'] = '0.00'
                        if 'latitude' in data.keys():
                            decimal_points = len(data['latitude']) - data['latitude'].rfind('.') - 1
                            if decimal_points > 6:
                                data['latitude'] = data['latitude'][:(len(data['latitude']) - (decimal_points-6))]
                        if 'longitude' in data.keys():
                            decimal_points = len(data['longitude']) - data['longitude'].rfind('.') - 1
                            if decimal_points > 6:
                                data['longitude'] = data['longitude'][:(len(data['longitude']) - (decimal_points-6))]
                    except:
                        pass
                return super(ODESerializer, self).run_validation(data)

            def create(self, attrs, instance=None):
                return super(ODESerializer, self).create(attrs)

            class Meta(ss.Meta):
                model = cls
                depth = 0
                fields = ('id', 'latitude', 'longitude', 'accuracy')

        return ODESerializer

    def __str__(self):
        return mark_safe('<a class="inline-link" href="http://maps.google.com/maps?z=17&q='
                         + str(self.latitude) + ','
                         + str(self.longitude) + '" target="_blank">'
                         + str(self.latitude) + ', ' + str(self.longitude) + '</a>')

    def clean(self):
        if self.latitude is None:
            self.latitude = Decimal(0.0)

        if self.longitude is None:
            self.longitude = Decimal(0.0)

        if self.accuracy is None:
            self.accuracy = Decimal(0.0)
