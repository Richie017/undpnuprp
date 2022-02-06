from blackwidow.core.models.common.custom_field import CustomField

__author__ = 'Ziaul Haque'


class CumulativeReportField(CustomField):
    class Meta:
        proxy = True
        app_label = 'approvals'
