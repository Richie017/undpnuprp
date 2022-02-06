import datetime
import re

from django.forms.widgets import Widget, Select
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe

__author__ = 'Tareq'

__all__ = ('MonthYearWidget',)

RE_DATE = re.compile(r'((\d\d?)-(\d\d?)-\d{4})$')


class MonthYearWidget(Widget):
    """
        A widget to split satetime widget into two select fields of month and year
    """
    none_value = (0, '---')
    month_field = '%s_month'
    year_field = '%s_year'

    def __init__(self, attrs=None, years=None, required=True):
        self.attrs = attrs or {}
        self.required = required
        if years:
            self.years = years
        else:
            this_year = datetime.date.today().year
            self.years = range(this_year - 25, this_year + 75)

    def render(self, name, value, attrs=None):
        try:
            year_val, month_val = value.year, value.month
        except AttributeError:
            year_val = month_val = None
            if isinstance(value, str):
                match = RE_DATE.match(value)
                if match:
                    day_val, month_val, year_val = [int(v) for v in match.groups()]
        if year_val is None:
            year_val = datetime.datetime.now().year
        if month_val is None:
            month_val = datetime.datetime.now().month

        output = []

        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name

        month_choices = MONTHS.items()
        local_attrs = self.attrs
        local_attrs.update({'id':self.month_field % id_})
        s = Select(choices=month_choices)
        select_html = s.render(self.month_field % name, month_val, local_attrs)
        output.append(select_html)

        year_choices = [(i, i) for i in self.years]
        local_attrs['id'] = self.year_field % id_
        s = Select(choices=year_choices)
        select_html = s.render(self.year_field % name, year_val, local_attrs)
        output.append(select_html)

        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        return '%s_month' % id_

    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        y = data.get(self.year_field % name)
        m = data.get(self.month_field % name)
        if y == m == "0":
            return None
        if y and m:
            return '%s-%s-%s' % (1, m, y)
        return data.get(name, None)
