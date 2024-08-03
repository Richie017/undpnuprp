"""
    Written by tareq on 7/24/18
"""
from enum import Enum

from django.utils.safestring import mark_safe

__author__ = 'Tareq'


class QueueElementStatusEnum(Enum):
    SCHEDULED = 'Scheduled'
    PROCESSING = 'Processing'
    COMPLETED = 'Completed'
    ERROR = 'Error'

    @classmethod
    def render(cls, item):
        _icon = ""
        _class = ""
        if item == cls.SCHEDULED.value:
            _class = 'warning'
            item = 'Scheduled'
        if item == cls.COMPLETED.value:
            _class = 'success'
            item = 'Completed'
        if item == cls.ERROR.value:
            _class = 'error'
            item = 'Error'
        if item == cls.PROCESSING.value:
            _class = 'info'
            item = 'Processing'
            _icon = "<i class='icon-spinner-live'></i>"
        return mark_safe("<span class='text-" + _class + "'>" + _icon + "<strong> " + item + "</strong></span>")