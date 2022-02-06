"""
Created by tareq on 2/20/18
"""
from blackwidow.engine.decorators.enable_export import enable_export
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.approvals.models.grantees.eligible_grantees.eligible_education_grantee import EligibleEducationGrantee

__author__ = 'Tareq'


@decorate(is_object_context, enable_export,
          route(route='eligible-education-drop-out-grantee', group='Local Economy Livelihood and Financial Inclusion',
                module=ModuleEnum.Analysis,
                group_order=3, display_name='Eligibles for Education Grant (Reduce Dropout)', item_order=3))
class EligibleEducationDropOutGrantee(EligibleEducationGrantee):
    class Meta:
        app_label = 'approvals'
        proxy = True
