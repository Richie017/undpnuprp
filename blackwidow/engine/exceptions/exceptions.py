from rest_framework.exceptions import APIException

__author__ = 'ruddra'


class BWException(Exception):
    message = 'An error occurred.'

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class EntityNotDeletableException(BWException):
    pass


class EntityForceDeletableException(EntityNotDeletableException):
    pass


class NotEnoughPermissionException(BWException):
    pass


class EntityNotEditableException(BWException):
    pass


class DBLockException(BWException):
    pass


class NullException(BWException):
    pass
