from django.utils.safestring import mark_safe

from blackwidow.core.models.contracts.base import DomainEntity


__author__ = 'Mahmud'

from django.db import models


class EducationalQualification(DomainEntity):
    degree = models.CharField(max_length=200, default="")
    year = models.CharField(max_length=200, default="")
    institute = models.CharField(max_length=200, default="")
    board = models.CharField(max_length=200, default="")
    result = models.CharField(max_length=200, default="")

    def __str__(self):
        return mark_safe(self.degree + '<br/>' +
                         self.year + '<br/>' +
                         self.institute + '<br/>' +
                         self.board + '<br/>' +
                         self.result)

    @classmethod
    def get_serializer(cls):
        ss = DomainEntity.get_serializer()

        class Serializer(ss):
            class Meta(DomainEntity.Meta):
                model = cls
                fields = ( 'id', 'code', 'degree', 'year', 'institute', 'board', 'result', 'date_created' )
        return Serializer



