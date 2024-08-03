"""
Created by tareq on 2/15/18
"""
from blackwidow.core.models.common.custom_field import CustomField
from blackwidow.engine.decorators import save_audit_log
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.enums.reachout_level_enum import ReachoutLevelEnum

__author__ = 'Tareq'


@decorate(save_audit_log, expose_api('monthly-report-fields'))
class MonthlyReportField(CustomField):
    class Meta:
        proxy = True
        app_label = 'approvals'

    @classmethod
    def get_model_api_queryset(cls, queryset=None):
        return queryset.filter(reachout_level=ReachoutLevelEnum.All.value)

