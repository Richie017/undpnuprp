from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.reports.models.base.base import Report

__author__ = 'Tareq'


class ReportForm(GenericFormMixin):
    class Meta(GenericFormMixin):
        model = Report
        fields = []
