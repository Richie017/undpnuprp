from django.forms.models import ModelChoiceField

from undp_nuprp.reports.extensions.fields.base_field import BaseReportField


class ModelSingleObjectField(BaseReportField, ModelChoiceField):
    def __init__(self, *args, **kwargs):
        super(ModelSingleObjectField, self).__init__(*args, **kwargs)
