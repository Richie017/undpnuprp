"""
Created by tareq on 10/3/17
"""
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.nuprp_admin.models.reports.grantees_follow_up.grantee_follow_up import GranteeFollowUp

__author__ = 'Tareq'


class GranteeFollowUpForm(GenericFormMixin):
    class Meta(GenericFormMixin.Meta):
        model = GranteeFollowUp
