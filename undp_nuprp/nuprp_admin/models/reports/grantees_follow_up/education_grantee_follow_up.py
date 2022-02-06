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
          route(route='education-grantee-follow-up', group='Grants', module=ModuleEnum.Execute,
                display_name='Edunaction Grant Follow Up', group_order=2, item_order=3))
class EducationGranteeFollowUp(GranteeFollowUp):
    first_year_school = models.CharField(blank=True, max_length=256)
    current_year_school = models.CharField(blank=True, max_length=256)
    status_of_education = models.TextField(blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        app_label = 'nuprp_admin'

    @classmethod
    def table_columns(cls):
        return ('render_code', 'grantee', 'date_of_last_installment',
                'first_year_school:Year of schooling during first instalment of grant',
                'current_year_school:Current year of schooling (at the time of reporting)', 'status_of_education',
                'date_created:Created On')

    @property
    def details_config(self):
        details = OrderedDict()
        details['grantee'] = self.grantee
        details['town'] = self.grantee.town
        details['date_of_last_installment'] = self.date_of_last_installment
        details['Year of schooling during first instalment of grant'] = self.first_year_school
        details['Current year of schooling (at the time of reporting)'] = self.current_year_school
        details['status_of_education'] = self.status_of_education if self.status_of_education else 'N/A'
        details['remarks'] = self.remarks if self.remarks else 'N/A'
        return details
