from collections import OrderedDict

from django.apps import apps
from django.db.models import Q

from blackwidow.core.models import ApprovalProcess
from blackwidow.core.models.common.choice_options import ApprovalStatus
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.models.alerts.savings_and_credit_alert_base.savings_and_credit_alert_base import \
    SavingsAndCreditAlertBase

get_model = apps.get_model

__author__ = "Shama"


@decorate(is_object_context,
          route(route='savings-and-credit-alert', group='Savings and Credit Alerts',
                module=ModuleEnum.Alert, display_name='Single Alert CDC wise', group_order=3, item_order=1))
class SavingsAndCreditReportAlert(SavingsAndCreditAlertBase):
    class Meta:
        app_label = 'nuprp_admin'
        proxy = True

    @property
    def render_CDC(self):
        try:
            return get_model(self.app_label, self.model).objects.get(pk=self.object_id)
        except:
            return 'Not Found'

    @property
    def render_city(self):
        try:
            cdc = get_model(self.app_label, self.model).objects.get(pk=self.object_id)
            return cdc.render_city_corporation
        except:
            return "N/A"

    @classmethod
    def search_city(cls, queryset, value):
        return queryset.filter(
            Q(cdc_reports__cdc__address__geography__parent__name__icontains=value) |
            Q(scg_reports__scg__address__geography__name__icontains=value)
        )

    @property
    def render_auto_approval_time(self):
        try:
            if self.cdc_reports.exists():
                cdc_report_id = self.cdc_reports.order_by('-on_spot_creation_time').first().pk
                approval_process = ApprovalProcess.get_objects_by_model_name(
                    model_name='CDCMonthlyReport', app_label='approvals'
                ).order_by('-last_updated').first()
                approval_action = approval_process.actions.filter(
                    status=ApprovalStatus.Approved.value, object_id=cdc_report_id).order_by('-last_updated').first()
                return self.render_timestamp(approval_action.last_updated)
            else:
                scg_report_id = self.scg_reports.order_by('-on_spot_creation_time').first().pk
                approval_process = ApprovalProcess.get_objects_by_model_name(
                    model_name='SCGMonthlyReport', app_label='approvals'
                ).order_by('-last_updated').first()
                approval_action = approval_process.actions.filter(
                    status=ApprovalStatus.Approved.value, object_id=scg_report_id).order_by('-last_updated').first()
                return self.render_timestamp(approval_action.last_updated)
        except:
            return 'Not yet approved'

    @classmethod
    def table_columns(cls):
        return ['render_code', 'render_city', 'render_CDC', 'alert_detail:Description',
                'alert_creation_time:Created On', 'render_auto_approval_time']

    @classmethod
    def get_object_inline_buttons(cls):
        return []

    @property
    def general_info(self):
        from undp_nuprp.nuprp_admin.models import CDC
        details = OrderedDict()
        cdc_obj = CDC.objects.filter(pk=self.object_id).first()
        details['CDC_name'] = cdc_obj.name
        details['type'] = cdc_obj.remarks
        details['assigned_community_facilitator'] = cdc_obj.render_community_facilitator
        details['CDC_cluster'] = cdc_obj.parent
        details['city_corporation'] = cdc_obj.render_city_corporation
        details['CDC_ID'] = cdc_obj.assigned_code
        details['primary_groups'] = cdc_obj.render_total_PG
        return details

    @property
    def details_config(self):
        d = OrderedDict()
        d['General Information'] = self.general_info
        return d

    @property
    def tabs_config(self):
        from undp_nuprp.approvals.models import SCGMonthlyReport, CDCMonthlyReport
        return [
            TabView(
                title='CDC Report(s)',
                access_key='cdc_reports',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model=CDCMonthlyReport,
                queryset=self.cdc_reports.all()
            ),
            TabView(
                title='SCG Report(s)',
                access_key='scg_reports',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model=SCGMonthlyReport,
                queryset=self.scg_reports.all()
            )
        ]
