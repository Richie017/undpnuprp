import datetime
from decimal import Decimal
from json.encoder import JSONEncoder
from types import MappingProxyType

__author__ = 'Mahmud'


class DynamicJsonObject(object):
    pass


class DynamicJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, (Decimal,)):
            return float(o)
        if isinstance(o, MappingProxyType):
            return str(o)
        if isinstance(o, (datetime.date,)):
            return dict(year=o.year, month=o.month, day=o.day)
        return o.__dict__