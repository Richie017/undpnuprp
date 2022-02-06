from enum import Enum

__author__ = 'bahar'

class SMSStatus(Enum):
    Pending = 0
    Delivered = 2
    Failed = 3
    NoResponse = 4

    @classmethod
    def get_enum_list(cls):
        enums = [(str(cls.Pending.value), cls.Pending.name),
                 (str(cls.Delivered.value), cls.Delivered.name),
                 (str(cls.Failed.value), cls.Failed.name),
                 (str(cls.NoResponse.value), cls.NoResponse.name)]
        return enums

    @classmethod
    def get_name(cls, value):
        if value == cls.Pending.value:
            return "Pending"
        if value == cls.Delivered.value:
            return "Delivered"
        if value == cls.Failed.value:
            return "Failed"
        if value == cls.NoResponse.value:
            return "No Response"
        return ""

