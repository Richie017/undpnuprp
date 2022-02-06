from django.db import transaction
from django.db.models.expressions import F

from blackwidow.core.models.common.location import Location
from undp_nuprp.approvals.models.savings_and_credits.logs.report_log import ActionTypeEnum
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.models.reports.savings_and_credit_report import SavingsAndCreditReport

__author__ = "Shama"


class PendingReport(SavingsAndCreditReport):

    @classmethod
    def distinct_fields(cls):
        return ['parent_id']

    @classmethod
    def table_columns(cls):
        return (
            'render_code', 'scg:SCG', 'render_primary_group', 'render_for_month', 'date_created:Report Created',
            'created_by', 'render_total_balance', 'last_updated')

    @classmethod
    def show_approve_button_first_level(self):
        return True

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete, ViewActionEnum.Approve]

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
            ),
            dict(
                name='Delete',
                action='delete',
                icon='fbx-rightnav-delete',
                ajax='0',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Delete),
                classes='manage-action all-action confirm-action',
                parent=None
            )
        ]

    @property
    def tabs_config(self):
        pending_report_versions = PendingReport.objects.filter(parent_id=self.parent_id).order_by('-date_created')
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
                related_model=PendingReport,
                queryset=PendingReport.objects.filter(id=_version.pk)
            )]
            version_index -= 1
        return tabs

    @classmethod
    def get_serializer(cls):
        IUSerializer = SavingsAndCreditReport.get_serializer()

        class PendingReportSerializer(IUSerializer):
            location = Location.get_serializer()()

            def create(self, attrs):
                from undp_nuprp.approvals.models.savings_and_credits.logs.report_log import SavingsAndCreditReportlog
                with transaction.atomic():
                    self.instance = super(PendingReportSerializer, self).create(attrs=attrs)
                    self.instance.city = self.instance.scg.address.geography.parent
                    self.instance.parent = self.instance
                    existing_pending_reports = PendingReport.objects.filter(
                        year=self.instance.year,
                        month=self.instance.month,
                        scg_id=self.instance.scg.id
                    )
                    if existing_pending_reports.exists():
                        if existing_pending_reports.filter(
                                parent_id=F('id')).exists():
                            existing_report_obj = existing_pending_reports.filter(
                                parent_id=F('id')).first()
                            self.instance.parent_id = existing_report_obj.id
                            self.instance.parent_tsync_id = existing_report_obj.tsync_id
                            SavingsAndCreditReportlog.create_report_log(report=self.instance.pk,
                                                                        action=ActionTypeEnum.Updated.value)
                            self.instance.save()
                        else:
                            self.instance.parent_id = self.instance.id
                            self.instance.parent_tsync_id = self.instance.tsync_id
                            SavingsAndCreditReportlog.create_report_log(report=self.instance.pk,
                                                                        action=ActionTypeEnum.Created.value)
                            self.instance.save()
                    else:
                        self.instance.parent_id = self.instance.id
                        self.instance.parent_tsync_id = self.instance.tsync_id
                        SavingsAndCreditReportlog.create_report_log(report=self.instance.pk,
                                                                    action=ActionTypeEnum.Created.value)
                        self.instance.save()
                return self.instance

            class Meta:
                model = cls
                fields = 'id', 'tsync_id', 'year', 'month', 'scg', 'deposited_savings', 'withdrawal_savings', \
                         'loan_disbursed_number', 'loan_disbursed', 'loan_repaid', 'outstanding_loans', \
                         'overdue_loans', 'passbook_update', 'passbook_cdc_inconsistency', 'area_inconsistency', \
                         'service_charges', 'admission_fees', 'bank_interest', 'bank_charges', 'other_expenditure', \
                         'bank_balance', 'cash_in_hand', 'remarks', 'location', 'last_updated'

        return PendingReportSerializer

    class Meta:
        app_label = 'nuprp_admin'
        proxy = True
