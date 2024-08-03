from collections import OrderedDict

__author__ = 'ziaul'


def fields_ordering(fields=OrderedDict(), fields_order=[]):
    # This function takes form fields and fields order as inputs and returns ordered fields based on fields order
    ordered_fields = OrderedDict()
    for field_name in fields_order:
        try:
            ordered_fields[field_name] = fields[field_name]
        except Exception as exp:
            pass
    return ordered_fields

