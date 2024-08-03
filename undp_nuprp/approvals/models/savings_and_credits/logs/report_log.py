from enum import Enum

from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = "Shama"


class ActionTypeEnum(Enum):
    Created = 'Created'
    Updated = 'Updated'
    Approved = 'Approved'

    @classmethod
    def get_enum_list(cls):
        enums = [(_enum.value, _enum.name) for _index, _enum in enumerate(cls)]
        return enums


@decorate(is_object_context,
          route(route='scg-report-logs', group='Logs', display_name='SCG Report Log', module=ModuleEnum.Settings))
class SavingsAndCreditReportlog(OrganizationDomainEntity):
    scg_report = models.ForeignKey('approvals.SCGMonthlyReport', null=True, on_delete=models.SET_NULL)
    action_type = models.CharField(max_length=200, blank=True)

    @property
    def render_savings_and_credit_group(self):
        return self.scg_report.scg if self.scg_report else 'N/A'

    @property
    def render_report_date(self):
        return self.scg_report.render_for_month

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Delete]

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details, ViewActionEnum.Delete]

    def details_link_config(self, **kwargs):
        return [
            dict(
                name='Delete',
                action='delete',
                icon='fbx-rightnav-delete',
                ajax='0',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Delete),
                classes='manage-action all-action confirm-action',
            )
        ]

    @classmethod
    def table_columns(cls):
        return ('render_code', 'scg_report', 'render_savings_and_credit_group', 'render_report_date',
                'action_type', 'date_created:Action Time', 'created_by:Action By')

    @classmethod
    def create_report_log(cls, report=None, action=ActionTypeEnum.Updated.value):
        report_log = SavingsAndCreditReportlog(scg_report_id=report, action_type=action)
        report_log.save()

    class Meta:
        app_label = 'approvals'
