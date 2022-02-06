from enum import Enum

__author__ = 'bahar'

class Rating(Enum):
    Terrible = 1
    Bad = 2
    OK = 3
    Good = 4
    Excellent = 5

    @classmethod
    def get_enum_list(cls):
        enums = [(str(cls.Terrible.value), cls.Terrible.name),
                 (str(cls.Bad.value), cls.Bad.name),
                 (str(cls.OK.value), cls.OK.name),
                 (str(cls.Good.value), cls.Good.name),
                 (str(cls.Excellent.value), cls.Excellent.name)]
        return enums

    @classmethod
    def get_name(cls, value):
        if value == cls.Terrible.value:
            return "Terrible"
        if value == cls.Bad.value:
            return "Bad"
        if value == cls.OK.value:
            return "OK"
        if value == cls.Good.value:
            return "Good"
        if value == cls.Excellent.value:
            return "Excellent"
        return ""

