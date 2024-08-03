from enum import Enum

__author__ = 'Tareq'


class SurveyStatusEnum(Enum):
    Draft = 0
    Published = 1
    Completed = 2

    @classmethod
    def get_status_name(cls, value):
        if value == cls.Draft.value:
            return cls.Draft.name
        if value == cls.Published.value:
            return cls.Published.name
        if value == cls.Completed.value:
            return cls.Completed.name
