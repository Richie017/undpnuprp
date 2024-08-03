from enum import Enum

__author__ = 'Tareq'


class ApprovedStateEnum(Enum):
    Pending = 0
    Approved = 1
    Rejected = 2
    On_hold = 3

    def __str__(self):
        self.name

    @classmethod
    def get_name_by_value(cls, value=0):
        if value == cls.Pending.value:
            return cls.Pending.name
        if value == cls.Approved.value:
            return cls.Approved.name
        if value == cls.Rejected.value:
            return cls.Rejected.name
        if value == cls.On_hold.value:
            return cls.On_hold.name
