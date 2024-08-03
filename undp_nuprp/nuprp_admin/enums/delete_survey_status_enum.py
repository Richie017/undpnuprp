from enum import Enum


class DeleteSurveyStatusEnum(Enum):
    SCHEDULED = 'Scheduled'
    RUNNING = 'Running'
    COMPLETED = 'Completed'
    FAILED = 'Failed'
