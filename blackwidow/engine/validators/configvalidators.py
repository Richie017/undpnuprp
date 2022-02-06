from blackwidow.engine.exceptions.exceptions import BWException, NullException

__author__ = 'ruddra'

import datetime


class ConfigValidator(object):
    @staticmethod
    def validate(config, value):
        if value == None:
            raise NullException("Value is null.")
        return True


# validate boolean values against config provided
class BooleanValidator(ConfigValidator):
    @staticmethod
    def validate(config, value):
        return True


#validate datetime values against config provided
class DateTimeValidator(ConfigValidator):
    @staticmethod
    def validate(config, value):
        dval = datetime.datetime.strptime(str(value), "%d/%m/%Y").date()
        if not config['allowFutureDate'] and dval > datetime.date.today():
            raise BWException("Future date is not supported for " + config['display'])
            return False
        if not config['allowCurrentDate'] and dval == datetime.date.today():
            raise BWException("Current date is not supported for " + config['display'])
            return False
        if not config['allowPastDate'] and dval < datetime.date.today():
            raise BWException("Past date is not supported for " + config['display'])
            return False
        return True


class DataValidator(ConfigValidator):
    @staticmethod
    def validate(config, value):
        return True