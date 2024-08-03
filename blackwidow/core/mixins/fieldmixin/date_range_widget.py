__author__ = 'Shamil'

# Created by shamilsakib at 8/20/2016
from django.forms import *


class DateRangeField(CharField):
    def __init__(self, *args, **kwargs):
        super(DateRangeField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        # todo Convert Date Range Value to time stamp tuple
        return value
