"""
Created by tareq on 12/26/17
"""
from enum import Enum

__author__ = 'Tareq'


class ScheduledTaskStatusEnum(Enum):
    SCHEDULED = 'Scheduled'
    RUNNING = 'Running'
    SUCCESS = 'Success'
    ERROR = 'Error'
