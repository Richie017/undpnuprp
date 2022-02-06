from django.db import models

from blackwidow.core.models.contracts.base import DomainEntity

__author__ = 'Jawad, Ziaul'


class ClientSupporter(DomainEntity):
    name = models.CharField(max_length=200)
    relation = models.CharField(max_length=200, default='')
    telephone = models.CharField(max_length=100, blank=True, null=True, default=None)

    @classmethod
    def get_serializer(cls):
        ss = DomainEntity.get_serializer()

        class Serializer(ss):
            class Meta(ss.Meta):
                model = cls
                fields = ('id', 'name', 'relation', 'telephone')

        return Serializer

    def __str__(self):
        result = self.name
        result += ",<br/><em>relation: </em>" + str(self.relation)
        result += ',<br/><em>telephone: </em>' + str(self.telephone)
        return result
