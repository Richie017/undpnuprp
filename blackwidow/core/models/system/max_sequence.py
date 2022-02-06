from django.db import models

__author__ = 'Mahmud'


class MaxSequence(models.Model):
    context = models.CharField(max_length=1000)
    value = models.BigIntegerField(default=1)

    _decorators = {}

    class Meta:
        pass

