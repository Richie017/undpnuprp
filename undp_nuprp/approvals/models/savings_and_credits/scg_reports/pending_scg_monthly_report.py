"""
Created by tareq on 2/15/18
"""
from django.db import transaction
from django.db.models import F

from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.decorators import save_audit_log
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.models import ActionTypeEnum
from undp_nuprp.approvals.models.savings_and_credits.scg_reports.scg_monthly_report import SCGMonthlyReport

__author__ = 'Tareq'


@decorate(is_object_context, save_audit_log, expose_api('pending-scg-monthly-report'),
          route(route='pending-scg-monthly-report', group='Savings & Credit Reports', module=ModuleEnum.Execute,
                display_name='Pending SCG Reports', group_order=1, item_order=1))
class PendingSCGMonthlyReport(SCGMonthlyReport):
    class Meta:
        app_label = 'approvals'
        proxy = True

    @classmethod
    def distinct_fields(cls):
        return ['parent_id']

    @classmethod
    def show_approve_button_first_level(cls):
        return True

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Approve, ViewActionEnum.Delete]

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details, ViewActionEnum.Delete]

    def details_link_config(self, **kwargs):
        latest_report_id = PendingSCGMonthlyReport.objects.filter(
            parent_id=self.parent_id).order_by('-on_spot_creation_time').first().id
        link_config = list()
        if latest_report_id == self.id:
            link_config.append(
                dict(
                    name='Edit',
                    action='edit',
                    icon='fbx-rightnav-edit',
                    ajax='0',
                    url_name=self.__class__.get_route_name(action=ViewActionEnum.Edit)
                )
            )
        link_config.append(
            dict(
                name='Approve',
                action='approve',
                icon='fbx-rightnav-tick',
                ajax='0',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Approve),
                classes='manage-action all-action confirm-action',
            ))
        link_config.append(
            dict(
                name='Delete',
                action='delete',
                icon='fbx-rightnav-delete',
                ajax='0',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Delete),
                classes='manage-action all-action confirm-action',
                parent=None
            ))
        return link_config

    @property
    def tabs_config(self):
        pending_report_versions = PendingSCGMonthlyReport.objects.filter(parent_id=self.parent_id).order_by(
            '-on_spot_creation_time')
        version_number = pending_report_versions.count()
        tabs = []
        version_index = version_number
        for _version in pending_report_versions:
            tabs += [TabView(
                title='Version ' + str(
                    version_index) + ' (Pending Report)'
                if version_index != version_number else 'Latest Version (Pending Report)',
                access_key='pending_reports' + str(version_index),
                route_name=self.__class__.get_route_name(action=ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model=PendingSCGMonthlyReport,
                queryset=PendingSCGMonthlyReport.objects.filter(id=_version.pk)
            )]
            version_index -= 1
        return tabs

    @classmethod
    def get_serializer(cls):
        _SCGMonthlyReportSerializer = SCGMonthlyReport.get_serializer()

        class Serializer(_SCGMonthlyReportSerializer):
            def create(self, attrs):
                from undp_nuprp.approvals.models.savings_and_credits.logs.report_log import SavingsAndCreditReportlog
                from undp_nuprp.approvals.models.savings_and_credits.scg_reports.approved_scg_monthly_report import ApprovedSCGMonthlyReport
                with transaction.atomic():
                    _year = attrs['year']
                    _month = attrs['month']
                    _scg = attrs['scg']

                    # return existing approved report to avoid pending scg report version creation
                    existing_approved_reports = ApprovedSCGMonthlyReport.objects.filter(
                        year=_year,
                        month=_month,
                        scg=_scg
                    )
                    if existing_approved_reports:
                        return existing_approved_reports.first()

                    self.instance = super(Serializer, self).create(attrs=attrs)
                    self.instance.parent = self.instance
                    existing_pending_reports = PendingSCGMonthlyReport.objects.filter(
                        year=self.instance.year,
                        month=self.instance.month,
                        scg_id=self.instance.scg_id
                    )
                    if existing_pending_reports.exists():
                        if existing_pending_reports.filter(parent_id=F('id')).exists():
                            existing_report_obj = existing_pending_reports.filter(parent_id=F('id')).first()
                            self.instance.parent_id = existing_report_obj.id
                            self.instance.parent_tsync_id = existing_report_obj.tsync_id
                            SavingsAndCreditReportlog.create_report_log(
                                report=self.instance.pk, action=ActionTypeEnum.Updated.value)
                            self.instance.save()
                        else:
                            self.instance.parent_id = self.instance.id
                            self.instance.parent_tsync_id = self.instance.tsync_id
                            SavingsAndCreditReportlog.create_report_log(
                                report=self.instance.pk, action=ActionTypeEnum.Created.value)
                            self.instance.save()
                    else:
                        self.instance.parent_id = self.instance.id
                        self.instance.parent_tsync_id = self.instance.tsync_id
                        SavingsAndCreditReportlog.create_report_log(
                            report=self.instance.pk, action=ActionTypeEnum.Created.value)
                        self.instance.save()
                return self.instance

            class Meta(_SCGMonthlyReportSerializer.Meta):
                model = cls

        return Serializer
