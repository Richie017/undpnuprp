from datetime import date

from dateutil.relativedelta import relativedelta


def calculate_birth_date(age=0):
    """
    :param age: take integer value
    :return: date of birth(datetime object)
    """

    _today = date.today()
    _birth_date = _today - relativedelta(years=age)
    return _birth_date


def calculate_age(born):
    """
    :param born: take datetime object
    :return: age as integer
    """
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
