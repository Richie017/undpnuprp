__author__ = 'shamil'

# return all of its declared Enum values as Dictinary.
def get_enum_items_as_dict(enum):
    return dict(enum.__members__)

# will give you the specific Enum item based on provided property name with value to be matched
def get_enum_by_property_value(enum, property, value):
    enum_dict = get_enum_items_as_dict(enum)
    for key in enum_dict.keys():
        if enum_dict.get(key).value[property] == value:
            return enum_dict.get(key)
    return None
