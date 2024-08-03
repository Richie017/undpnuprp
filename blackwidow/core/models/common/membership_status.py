from enum import Enum

__author__ = 'bahar'

class MembershipStatus(Enum):
    Active = 0
    Suspended = 1
    Expired = 2
    Cancelled = 3

    @classmethod
    def get_enum_list(cls):
        enums = [(str(cls.Active.value), cls.Active.name),
                 (str(cls.Suspended.value), cls.Suspended.name),
                 (str(cls.Expired.value), cls.Expired.name),
                 (str(cls.Cancelled.value), cls.Cancelled.name)]
        return enums

    @classmethod
    def get_name(cls, value):
        if value == cls.Active.value:
            return "Active"
        if value == cls.Suspended.value:
            return "Suspended"
        if value == cls.Expired.value:
            return "Expired"
        if value == cls.Cancelled.value:
            return "Cancelled"
        return ""


class PrimaryGroupMemberStatus(Enum):
    Active = 'Active'
    Dead = 'Dead'
    Migrated = 'Migrated'
    Dropout = 'Dropout'

    @classmethod
    def get_enum_list(cls):
        enums = [(str(cls.Active.value), cls.Active.name),
                 (str(cls.Dead.value), cls.Dead.name),
                 (str(cls.Migrated.value), cls.Migrated.name),
                 (str(cls.Dropout.value), cls.Dropout.name)]
        return enums


class TransactionStatus(Enum):
    Opened = 0
    Suspended = 1
    Closed = 2
    Cancelled = 3

    @classmethod
    def get_enum_list(cls):
        enums = [(str(cls.Opened.value), cls.Opened.name),
                 (str(cls.Suspended.value), cls.Suspended.name),
                 (str(cls.Closed.value), cls.Closed.name),
                 (str(cls.Cancelled.value), cls.Cancelled.name)]
        return enums

    @classmethod
    def get_name(cls, value):
        if value == cls.Opened.value:
            return "Opened"
        if value == cls.Suspended.value:
            return "Suspended"
        if value == cls.Closed.value:
            return "Closed"
        if value == cls.Cancelled.value:
            return "Cancelled"
        return ""

