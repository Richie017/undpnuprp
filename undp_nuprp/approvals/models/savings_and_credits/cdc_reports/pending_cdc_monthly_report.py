"""
Created by tareq on 2/15/18
"""
from django.db import transaction
from django.db.models import F

from blackwidow.core.models import ErrorLog, CustomFieldValue
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.decorators import save_audit_log
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.models import CDCMonthlyReportField
from undp_nuprp.approvals.models.savings_and_credits.cdc_reports.cdc_monthly_report import CDCMonthlyReport
import re

__author__ = 'Tareq'


@decorate(is_object_context, save_audit_log, expose_api('pending-cdc-monthly-report'),
          route(route='pending-cdc-monthly-report', group='Savings & Credit Reports', module=ModuleEnum.Execute,
                display_name='Pending CDC Reports', group_order=1, item_order=3))
class PendingCDCMonthlyReport(CDCMonthlyReport):
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
        return [ViewActionEnum.Delete]

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details, ViewActionEnum.Delete]

    def details_link_config(self, **kwargs):
        latest_report_id = PendingCDCMonthlyReport.objects.filter(
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
        pending_report_versions = PendingCDCMonthlyReport.objects.filter(parent_id=self.parent_id).order_by(
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
                related_model=PendingCDCMonthlyReport,
                queryset=PendingCDCMonthlyReport.objects.filter(id=_version.pk)
            )]
            version_index -= 1
        return tabs

    @classmethod
    def update_calculated_field_info(cls, instance=None, assigned_codes=list()):
        calculated_field_objects = CDCMonthlyReportField.objects.filter(assigned_code__in=assigned_codes)
        _pattern = re.compile(r'@(.+?)@')
        _calculated_value = 0
        for _calculated_field in calculated_field_objects:
            _formula = _calculated_field.formula
            _assigned_codes = _pattern.findall(_formula)
            for _assigned_code in _assigned_codes:
                _latest_entry = instance.field_values.filter(
                    field__assigned_code=_assigned_code
                ).order_by('-last_updated').first()
                _v = 0
                if _latest_entry and _latest_entry.value:
                    _v = _latest_entry.value
                _formula = _formula.replace('@' + _assigned_code + '@', str(_v))
            try:
                _calculated_value = eval(_formula)
            except Exception as exp:
                ErrorLog.log(exp)
            field_value_object = CustomFieldValue(value=_calculated_value, field_id=_calculated_field.id)
            field_value_object.save()
            instance.field_values.add(field_value_object)
        instance.is_calculative_field_updated = True
        instance.save()

    @classmethod
    def get_serializer(cls):
        _CDCMonthlyReportSerializer = CDCMonthlyReport.get_serializer()

        class Serializer(_CDCMonthlyReportSerializer):
            def create(self, attrs):
                from undp_nuprp.approvals.models.savings_and_credits.cdc_reports.approved_cdc_monthly_report import ApprovedCDCMonthlyReport
                with transaction.atomic():
                    _year = attrs['year']
                    _month = attrs['month']
                    _cdc = attrs['cdc']

                    # return existing approved report to avoid pending cdc report version creation
                    existing_approved_reports = ApprovedCDCMonthlyReport.objects.filter(
                        year=_year,
                        month=_month,
                        cdc=_cdc
                    )
                    if existing_approved_reports:
                        return existing_approved_reports.first()

                    self.instance = super(Serializer, self).create(attrs=attrs)
                    self.instance.parent = self.instance

                    existing_pending_reports = PendingCDCMonthlyReport.objects.filter(
                        year=self.instance.year,
                        month=self.instance.month,
                        cdc_id=self.instance.cdc_id
                    )
                    if existing_pending_reports.exists():
                        if existing_pending_reports.filter(
                                parent_id=F('id')).exists():
                            existing_report_obj = existing_pending_reports.filter(
                                parent_id=F('id')).first()
                            self.instance.parent_id = existing_report_obj.id
                            self.instance.parent_tsync_id = existing_report_obj.tsync_id
                            self.instance.save()
                        else:
                            self.instance.parent_id = self.instance.id
                            self.instance.parent_tsync_id = self.instance.tsync_id
                            self.instance.save()
                    else:
                        self.instance.parent_id = self.instance.id
                        self.instance.parent_tsync_id = self.instance.tsync_id
                        self.instance.save()
                return self.instance

            class Meta(_CDCMonthlyReportSerializer.Meta):
                model = cls

        return Serializer
