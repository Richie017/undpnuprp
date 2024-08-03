from blackwidow.core.models.contracts.base import DomainEntity

__author__ = 'Sohel'

from django.db import models


class WeekDay(DomainEntity):
    name = models.CharField(null=True,blank=True,max_length=200)

    def __str__(self):
        return self.name

    def get_choice_name(self):
        return self.code + ': ' + self.name

    @classmethod
    def get_serializer(cls):
        ss = DomainEntity.get_serializer()

        class Serializer(ss):
            class Meta(DomainEntity.Meta):
                model = cls
                fields = ( 'id', 'code', 'name', 'date_created' )
        return Serializer



