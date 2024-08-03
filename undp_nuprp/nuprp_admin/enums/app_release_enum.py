"""
    Created by tareq on 9/1/19
"""
from enum import Enum

from blackwidow.engine.extensions import bw_titleize

__author__ = 'Razon'


class AppReleaseUpdateTypeEnum(Enum):
    NotMandatory = 0
    Mandatory = 1

    @classmethod
    def get_choice_list(cls, include_null=True, empty_label='Select One'):
        """
        This method prepare list of  value, name tuples consisting the items of enums. This can be used for select
        (dropdown) field's options. This method can prepare choice list both with and without initial null value.
        :param include_null: if  true, the first item of the choice list will be an empty value (no pre-selected item)
        :param empty_label: the label to display for initial empty value ('Select One' by default)
        :return: The list of value,name tuple consisting the items of the enum
        """

        options = list()
        for e in cls:
            options.append((e.value, bw_titleize(e.name)))
        options = sorted(options, key=lambda x: x[1])
        if include_null:
            options = [(None, empty_label)] + options
        return options

    @classmethod
    def get_name_from_value(cls, value, default='N/A'):
        """
        Get the name (label) of enum from value
        :param value: value of the enum
        :param default: to return if no value is matched with enum's value
        :return: label of enum if value is found. default otherwise
        """
        for e in cls:
            if value == e.value:
                return bw_titleize(e.name)
        return default
