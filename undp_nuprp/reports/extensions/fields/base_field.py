from django.forms.fields import Field


class BaseReportField(Field):
    def __init__(self, *args, **kwargs):
        self.related_field = kwargs.pop('related_field', None)
        super(BaseReportField, self).__init__(*args, **kwargs)
