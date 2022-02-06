from enum import Enum

from blackwidow.core.models.contracts.base import DomainEntity
from blackwidow.engine.decorators.enable_trigger import enable_trigger
from blackwidow.engine.decorators.utility import decorate

__author__ = 'Mahmud, Sohel'


class PhoneNumberOwnerEnum(Enum):
    own = "own"
    husband = "husband"
    family = "family"
    neighbour = "neighbour"
    other = "other"


owner_choices = []
owner_choices += [(PhoneNumberOwnerEnum.own.value, PhoneNumberOwnerEnum.own.value.capitalize())]
owner_choices += [(PhoneNumberOwnerEnum.husband.value, PhoneNumberOwnerEnum.husband.value.capitalize())]
owner_choices += [(PhoneNumberOwnerEnum.family.value, PhoneNumberOwnerEnum.family.value.capitalize())]
owner_choices += [(PhoneNumberOwnerEnum.neighbour.value, PhoneNumberOwnerEnum.neighbour.value.capitalize())]
owner_choices += [(PhoneNumberOwnerEnum.other.value, PhoneNumberOwnerEnum.other.value.capitalize())]

from django.db import models


@decorate(enable_trigger)
class PhoneNumber(DomainEntity):
    @classmethod
    def get_owner_choices(cls):
        return owner_choices

    phone = models.CharField(max_length=100, blank=True, null=True, default=None)
    is_primary = models.BooleanField(default=0)
    owner = models.CharField(max_length=20, blank=False, choices=owner_choices, default=PhoneNumberOwnerEnum.own.value)

    @classmethod
    def get_serializer(cls):
        ss = DomainEntity.get_serializer()

        class Serializer(ss):
            class Meta(DomainEntity.Meta):
                model = cls
                fields = ('id', 'code', 'phone', 'owner', 'date_created')

        return Serializer

    def load_initial_data(self, **kwargs):
        super().load_initial_data(**kwargs)
        self.phone = "0123456789"

    def __str__(self):
        return self.code + " Owner: " + self.owner
