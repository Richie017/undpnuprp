from enum import Enum

__author__ = 'bahar'

class MembershipType(Enum):
    FullSubsidy = 0
    PartialSubsidy = 1
    SelfPaid = 2

    @classmethod
    def get_enum_list(cls):
        enums = [(str(cls.FullSubsidy.value), cls.get_name(cls.FullSubsidy.value)),
                 (str(cls.PartialSubsidy.value), cls.get_name(cls.PartialSubsidy.value)),
                 (str(cls.SelfPaid.value), cls.get_name(cls.SelfPaid.value))]
        return enums

    @classmethod
    def get_name(cls, value):
        if value == cls.FullSubsidy.value:
            return "Full Subsidy"
        if value == cls.PartialSubsidy.value:
            return "Partial Subsidy"
        if value == cls.SelfPaid.value:
            return "Self Paid"
        return ""

