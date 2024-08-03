import datetime
import time

from crequest.middleware import CrequestMiddleware
from django.utils import timezone

from settings import TIME_ZONE_DEFAULT_OFFSET

now = timezone.now()


class Clock(object):
    """
    System Clock
    """

    def __init__(self):
        pass

    @classmethod
    def get_timestamp_from_date(cls, datetime_string=''):
        """
        for getting timestamp from date use (datetimeobj).timestamp()*1000
        :param datetime_string:
        :return:
        """
        return datetime.datetime.strptime(datetime_string, "%d/%m/%Y %H:%M:%S").timestamp() * 1000

    @classmethod
    def convert_timestamp_to_datetime_str(cls, ts, _format='ms'):
        _ts = ts
        if _format == 'ms':
            _ts = ts / 1000
        return datetime.datetime.fromtimestamp(_ts).strftime('%d/%m/%Y %H:%M %p')

    @classmethod
    def millisecond_to_date_str(cls, timestamp, _is_millisecond=True, _format='%d/%m/%Y'):
        _timestamp = timestamp
        if _is_millisecond:
            _timestamp = timestamp / 1000
        return datetime.datetime.fromtimestamp(_timestamp).strftime(_format)

    @staticmethod
    def now():
        # return datetime.datetime(2014, 12, 31)
        return timezone.now()

    @staticmethod
    def utcnow():
        # return datetime.datetime(2014, 12, 31)
        return datetime.datetime.utcnow()

    @staticmethod
    def timestamp(_format='ms'):
        if _format == 'ms':
            return int(time.time() * 1000)
        return int(time.time())

    @staticmethod
    def localTzname():
        if time.daylight:
            offsetHour = time.altzone / 3600
        else:
            offsetHour = time.timezone / 3600
        return 'Etc/GMT%+d' % offsetHour

    @staticmethod
    def get_utc_from_local_time(value=None):
        return datetime.datetime.utcfromtimestamp(value / 1000)

    @staticmethod
    def get_user_local_time(value=None):
        request = CrequestMiddleware.get_request()
        user_tz_offset = request.c_tz_offset if request else TIME_ZONE_DEFAULT_OFFSET
        if value is None:
            return Clock.utcnow() - datetime.timedelta(minutes=int(user_tz_offset))
        else:
            time_value = datetime.datetime.utcfromtimestamp(value / 1000)
            return time_value - datetime.timedelta(minutes=int(user_tz_offset))

    @staticmethod
    def get_user_universal_time(value=None):
        request = CrequestMiddleware.get_request()
        user_tz_offset = request.c_tz_offset
        if value is None:
            return Clock.utcnow() + datetime.timedelta(minutes=int(user_tz_offset))
        else:
            time_value = datetime.datetime.utcfromtimestamp(value / 1000)
            return time_value + datetime.timedelta(minutes=int(user_tz_offset))

    @staticmethod
    def human_readable_time(time):
        # takes hour as an integer format and returns human readable time for corresponding hour
        if time == 0:
            return "12:00AM"
        if time == 12:
            return "12:00PM"
        if time >= 12:
            return str(time - 12) + ":00PM"
        else:
            return str(time) + ":00AM"

    @classmethod
    def date_range_from_str(cls, value=None):
        if value:
            date_range = value.replace(' ', '').split("-")
            from_date = to_date = None
            if len(date_range) > 0:
                from_date_string = date_range[0]
                from_date = datetime.datetime.strptime(from_date_string, "%d/%m/%Y").timestamp() * 1000
            if len(date_range) > 1:
                to_date_string = date_range[1]
                to_date = (datetime.datetime.strptime(to_date_string, "%d/%m/%Y") + datetime.timedelta(
                    1)).timestamp() * 1000

            return from_date, to_date
        return None, None

    @classmethod
    def date_range_from_str_no_timestamp(cls, value=None):
        if value:
            date_range = value.replace(' ', '').split("-")
            from_date = to_date = None
            if len(date_range) > 0:
                from_date_string = date_range[0]
                from_date = datetime.datetime.strptime(from_date_string, "%d/%m/%Y")
            if len(date_range) > 1:
                to_date_string = date_range[1]
                to_date = (datetime.datetime.strptime(to_date_string, "%d/%m/%Y") + datetime.timedelta(1))

            return from_date, to_date
        return None, None

    @classmethod
    def date_range_all_from_str(cls, value=None):
        if value:
            date_range = value.replace(' ', '').split("-")
            from_date_string = to_date_string = from_date = to_date = None
            if len(date_range) > 0:
                from_date_string = date_range[0]
                from_date = datetime.datetime.strptime(from_date_string, "%d/%m/%Y").timestamp() * 1000
            if len(date_range) > 1:
                to_date_string = date_range[1]
                to_date = (datetime.datetime.strptime(to_date_string, "%d/%m/%Y") + datetime.timedelta(
                    1)).timestamp() * 1000
            return from_date_string, to_date_string, from_date, to_date
        return None, None, None, None

    @classmethod
    def date_range_all_from_str_no_timestamp(cls, value=None):
        if value:
            date_range = value.replace(' ', '').split("-")
            from_date_string = to_date_string = from_date = to_date = None
            if len(date_range) > 0:
                from_date_string = date_range[0]
                from_date = datetime.datetime.strptime(from_date_string, "%d/%m/%Y")
            if len(date_range) > 1:
                to_date_string = date_range[1]
                to_date = (datetime.datetime.strptime(to_date_string, "%d/%m/%Y") + datetime.timedelta(1))
            return from_date_string, to_date_string, from_date, to_date
        return None, None, None, None
