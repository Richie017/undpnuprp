from collections import OrderedDict

from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context, save_audit_log
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.models.field_monitoring.field_monitoring_report import FieldMonitoringReport


@decorate(is_object_context, save_audit_log, route(
    route='submitted-field-monitoring-report', module=ModuleEnum.Analysis, group='Field Monitoring', group_order=8,
    item_order=2, display_name='Submitted Field Monitoring Report'
))
class SubmittedFieldMonitoringReport(FieldMonitoringReport):
    class Meta:
        app_label = 'approvals'
        proxy = True

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Edit, ViewActionEnum.Approve]

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Edit, ViewActionEnum.Details]

    def details_link_config(self, **kwargs):
        return [
            dict(
                name='Edit',
                action='edit',
                icon='fbx-rightnav-edit',
                ajax='0',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Edit)
            ),
            dict(
                name='Approve',
                action='approve',
                icon='fbx-rightnav-tick',
                ajax='0',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Approve),
                classes='manage-action all-action confirm-action',
            )
        ]

    def details_config(self):
        details = OrderedDict()
        details['detail_title'] = self.detail_title
        details['code'] = self.code
        details['city'] = self.city
        details['ward'] = self.ward
        details['date'] = self.date
        details['name'] = self.name
        details['designation'] = self.designation
        details['mission_objective'] = self.mission_objective
        details['output'] = self.render_output
        details['report_submitted'] = self.report_submitted
        details['Attachment'] = self.render_download_url
        details['followup_date'] = self.followup_date
        details['created_by'] = self.created_by
        details['date_created'] = self.render_timestamp(self.date_created)
        details['Last updated on'] = self.render_timestamp(self.last_updated)

        manager_comments = OrderedDict()
        manager_comments['international_technical_adviser'] = self.international_technical_adviser
        manager_comments['project_manager'] = self.project_manager
        manager_comments['monitoring_and_evaluation_specialist'] = self.monitoring_and_evaluation_specialist
        manager_comments['output_leads'] = self.output_leads
        manager_comments['others'] = self.others
        details['Management Comments'] = manager_comments
        return details
