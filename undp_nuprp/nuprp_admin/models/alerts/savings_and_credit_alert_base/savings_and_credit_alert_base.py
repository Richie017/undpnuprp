from django.db import models
from blackwidow.core.models import AlertConfig


class SavingsAndCreditAlertBase(AlertConfig):
    year = models.IntegerField(default=2010)
    month = models.IntegerField(default=1)
    day = models.IntegerField(default=1)
    cdc_reports = models.ManyToManyField('approvals.CDCMonthlyReport')
    scg_reports = models.ManyToManyField('approvals.SCGMonthlyReport')

    @property
    def get_inline_manage_buttons(self):
        return []

    @classmethod
    def table_columns(cls):
        return ['render_code', 'date_created', 'last_updated']

    class Meta:
        app_label = 'nuprp_admin'

