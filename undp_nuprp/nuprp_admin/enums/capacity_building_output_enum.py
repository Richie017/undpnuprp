"""
    Created by ahsan on 3/15/22
"""
from enum import Enum

__author__ = "Ahsan"


class CapacityBuildingOutputEnum(Enum):
    Output_1 = 1
    Output_2 = 2
    Output_3 = 3
    Output_4 = 4
    Output_5 = 5
    Other = 100

    @classmethod
    def get_name_from_value(cls, value, default='N/A'):
        """
        Get the name (label) of enum from value
        :param value: value of the enum
        :param default: to return if no value is matched with enum's value
        :return: label of enum if value is found. default otherwise
        """
        from blackwidow.engine.extensions.bw_titleize import bw_titleize

        for e in cls:
            if value == e.value:
                return bw_titleize(e.name)
        return default

    @classmethod
    def get_value_from_name_i(cls, name, default=None):
        """
        Get the value of enum from name (label) - case insensitive
        :param name: name (label) of enum
        :param default: to return if no name(label) is matched
        :return: value of enum if name if found. default otherwise
        """
        name = name.strip()
        from blackwidow.engine.extensions.bw_titleize import bw_titleize

        for e in cls:
            if name.lower() == e.name.lower() or name.lower() == bw_titleize(e.name).lower():
                return e.value
        return default

    @classmethod
    def get_value_from_name(cls, name, default=None):
        """
        Get the value of enum from name (label)
        :param name: name (label) of enum
        :param default: to return if no name(label) is matched
        :return: value of enum if name if found. default otherwise
        """
        from blackwidow.engine.extensions.bw_titleize import bw_titleize

        for e in cls:
            if name == e.name or name == bw_titleize(e.name):
                return e.value
        return default

    @classmethod
    def get_choice_list(cls, include_null=True, empty_label='Select One'):
        """
        This method prepare list of  value, name tuples consisting the items of enums. This can be used for select
        (dropdown) field's options. This method can prepare choice list both with and without initial null value.
        :param include_null: if  true, the first item of the choice list will be an empty value (no pre-selected item)
        :param empty_label: the label to display for initial empty value ('Select One' by default)
        :return: The list of value,name tuple consisting the items of the enum
        """
        from blackwidow.engine.extensions.bw_titleize import bw_titleize

        options = list()
        for e in cls:
            options.append((e.value, bw_titleize(e.name)))
        if include_null:
            options = [(None, empty_label)] + options
        return options


    def get_output_choice_list_from_object(object, include_null=True, empty_label='Select One'):
        """
        This method prepare list of  value, name tuples consisting the items of enums. This can be used for select
        (dropdown) field's options. This method can prepare choice list both with and without initial null value.
        :param include_null: if  true, the first item of the choice list will be an empty value (no pre-selected item)
        :param empty_label: the label to display for initial empty value ('Select One' by default)
        :return: The list of value,name tuple consisting the items of the enum
        """
        from blackwidow.engine.extensions.bw_titleize import bw_titleize

        options = list()
        for e in object:
            options.append((bw_titleize(e.output), bw_titleize(e.output)))
        if include_null:
            options = [(None, empty_label)] + options
        return options


    
    def get_title_choice_list_from_object(object, include_null=True, empty_label='Select One'):
        """
        This method prepare list of  value, name tuples consisting the items of enums. This can be used for select
        (dropdown) field's options. This method can prepare choice list both with and without initial null value.
        :param include_null: if  true, the first item of the choice list will be an empty value (no pre-selected item)
        :param empty_label: the label to display for initial empty value ('Select One' by default)
        :return: The list of value,name tuple consisting the items of the enum
        """
        from blackwidow.engine.extensions.bw_titleize import bw_titleize

        options = list()
        for e in object:
            options.append(( bw_titleize(e.title), bw_titleize(e.title)+'|'+bw_titleize(e.output)))
        if include_null:
            options = [(None, empty_label)] + options
        options.append(( bw_titleize("Other"), bw_titleize("Other")+'|'+bw_titleize("Output 1")))
        options.append(( bw_titleize("Other"), bw_titleize("Other")+'|'+bw_titleize("Output 2")))
        options.append(( bw_titleize("Other"), bw_titleize("Other")+'|'+bw_titleize("Output 3")))
        options.append(( bw_titleize("Other"), bw_titleize("Other")+'|'+bw_titleize("Output 4")))
        options.append(( bw_titleize("Other"), bw_titleize("Other")+'|'+bw_titleize("Output 5")))
        options.append(( bw_titleize("Other"), bw_titleize("Other")+'|'+bw_titleize("Output 6")))
       
        return options

    def get_output_choice_from_object(object, include_null=True, empty_label='Select One'):
        """
        This method prepare list of  value, name tuples consisting the items of enums. This can be used for select
        (dropdown) field's options. This method can prepare choice list both with and without initial null value.
        :param include_null: if  true, the first item of the choice list will be an empty value (no pre-selected item)
        :param empty_label: the label to display for initial empty value ('Select One' by default)
        :return: The list of value,name tuple consisting the items of the enum
        """
        from blackwidow.engine.extensions.bw_titleize import bw_titleize

        option = bw_titleize(object.output)
        return option


    
