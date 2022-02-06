"""
Created by tareq on 10/3/17
"""
from collections import OrderedDict

from django.db import models

from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.nuprp_admin.models.reports.grantees_follow_up.grantee_follow_up import GranteeFollowUp

__author__ = 'Tareq'


@decorate(is_object_context,
          route(route='business-grantee-follow-up', group='Grants', module=ModuleEnum.Execute,
                display_name='Business Grant Follow Up', group_order=2, item_order=2))
class BusinessGranteeFollowUp(GranteeFollowUp):
    before_employment_status = models.CharField(blank=True, max_length=256)
    current_employment_status = models.CharField(blank=True, max_length=256)
    remarks = models.TextField(blank=True)

    class Meta:
        app_label = 'nuprp_admin'

    @classmethod
    def table_columns(cls):
        return ('render_code', 'grantee', 'date_of_last_installment',
                'before_employment_status:Employment status immediately prior to receiving grant',
                'current_employment_status:Current employment status',
                'date_created:Created On')

    @property
    def details_config(self):
        details = OrderedDict()
        details['grantee'] = self.grantee
        details['town'] = self.grantee.town
        details['date_of_last_installment'] = self.date_of_last_installment
        details['Employment status immediately prior to receiving grant'] = self.before_employment_status
        details['Current employment status'] = self.current_employment_status
        details['remarks'] = self.remarks if self.remarks else 'N/A'
        return details
