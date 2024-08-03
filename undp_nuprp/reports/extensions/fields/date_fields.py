from django.forms.fields import DateTimeField

from undp_nuprp.reports.extensions.fields.base_field import BaseReportField


class StartDateTimeField(BaseReportField, DateTimeField):
    def __init__(self, *args, **kwargs):
        super(StartDateTimeField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        datetime = super(StartDateTimeField, self).to_python(value=value)
        if datetime:
            return datetime.timestamp() * 1000
        return datetime


class EndDateTimeField(BaseReportField, DateTimeField):
    def __init__(self, *args, **kwargs):
        super(EndDateTimeField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        datetime = super(EndDateTimeField, self).to_python(value=value)
        if datetime:
            return datetime.timestamp() * 1000
        return datetime
