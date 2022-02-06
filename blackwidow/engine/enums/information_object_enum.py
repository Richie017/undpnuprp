from enum import Enum

__author__ = 'Tareq'


class InformationNotificationEnum(Enum):
    none = 0
    all = 1
    mobile = 2
    email = 4

    @classmethod
    def get_choices(cls):
        return (
            (1, 'All'),
            (2, 'Mobile'),
            (3, 'Email'),
        )
