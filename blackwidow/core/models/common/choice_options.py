from enum import Enum

__author__ = 'bahar'

class YesNo(Enum):
    Yes = 0
    No = 1

    @classmethod
    def get_enum_list(cls):
        enums = [(str(cls.Yes.value), cls.Yes.name),
                 (str(cls.No.value), cls.No.name)]
        return enums

    @classmethod
    def get_name(cls, value):
        if value == cls.Yes.value:
            return "Yes"
        if value == cls.No.value:
            return "No"
        return ""


class ApprovalStatus(Enum):
    Approved = 0
    Rejected = 1
    Pending = 2
    StepBack = 3
    Restore = 4

    @classmethod
    def get_enum_list(cls):
        enums = [(str(cls.Approved.value), cls.Approved.name),
                 (str(cls.Rejected.value), cls.Rejected.name),
                 (str(cls.Pending.value), cls.Pending.name),
                 (str(cls.StepBack.value), cls.StepBack.name),
                 (str(cls.Restore.value), cls.Restore.name)]
        return enums

    @classmethod
    def get_name(cls, value):
        if value == cls.Approved.value:
            return "Approved"
        if value == cls.Rejected.value:
            return "Rejected"
        if value == cls.Pending.value:
            return "Pending"
        if value == cls.StepBack.value:
            return "StepBack"
        if value == cls.Restore.value:
            return "Restore"
        return ""

