"""
Created by tareq on 2/15/18
"""
from blackwidow.engine.decorators import save_audit_log
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.utility import decorate
from undp_nuprp.approvals.models.savings_and_credits.base.monthly_report_field import MonthlyReportField

__author__ = 'Tareq'


@decorate(save_audit_log, expose_api('cdc-monthly-report-fields'))
class CDCMonthlyReportField(MonthlyReportField):
    class Meta:
        proxy = True
        app_label = 'approvals'
