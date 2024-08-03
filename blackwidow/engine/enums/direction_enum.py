from enum import Enum

__author__ = 'Mahmud'

class DirectionEnum(Enum):
    FORWARD = 'forward'
    BACKWARD = 'backward'

    def __str__(self):
        return self.value