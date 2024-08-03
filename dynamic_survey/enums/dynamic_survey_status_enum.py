from enum import Enum

__author__ = 'Tareq'


class DynamicSurveyStatusEnum(Enum):
    Draft = 0
    Published = 1
    Disabled = 2
    Enabled = 3
    Completed = 4

    @classmethod
    def get_status_name(cls, value):
        if value == cls.Draft.value:
            return cls.Draft.name
        if value == cls.Published.value:
            return cls.Published.name
        if value == cls.Disabled.value:
            return cls.Disabled.name
        if value == cls.Enabled.value:
            return cls.Enabled.name
        if value == cls.Completed.value:
            return cls.Completed.name
