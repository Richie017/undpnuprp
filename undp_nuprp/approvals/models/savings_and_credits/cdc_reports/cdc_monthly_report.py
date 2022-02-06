"""
Created by tareq on 2/15/18
"""
import calendar
from collections import OrderedDict
from datetime import datetime

from django.db import models

from blackwidow.core.models import Organization, AlertGroup, ErrorLog
from blackwidow.core.models.common.custom_field import CustomFieldValue
from blackwidow.core.models.common.location import Location
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.utility import decorate, save_audit_log
from blackwidow.engine.extensions import Clock
from undp_nuprp.nuprp_admin.models.alerts.savings_and_credit_report_alert import SavingsAndCreditReportAlert
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc import CDC

__author__ = 'Tareq, Ziaul Haque'


@decorate(save_audit_log, expose_api('cdc-monthly-report'))
class CDCMonthlyReport(OrganizationDomainEntity):
    year = models.IntegerField(default=2010)
    month = models.IntegerField(default=1)
    cdc = models.ForeignKey(CDC, null=True, on_delete=models.SET_NULL)
    field_values = models.ManyToManyField('core.CustomFieldValue')
    location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)
    remarks = models.CharField(max_length=300, null=True)
    parent = models.ForeignKey('approvals.CDCMonthlyReport', null=True)
    parent_tsync_id = models.CharField(max_length=60, null=True)
    on_spot_creation_time = models.BigIntegerField(default=0)  # when this version/object is being created
    is_calculative_field_updated = models.BooleanField(default=False,
                                                       editable=False)  # calculative field value's update status
    is_baseline = models.BooleanField(default=False, editable=False)  # distinguish between baseline and monthly report

    class Meta:
        app_label = 'approvals'

    @classmethod
    def distinct_fields(cls):
        return ['parent_id']

    def save(self, *args, organization=None, **kwargs):
        super(CDCMonthlyReport, self).save(*args, organization=organization, **kwargs)
        if self.on_spot_creation_time == 0:
            self.on_spot_creation_time = self.date_created  # update on_spot_creation_time field by date_created
            self.save()

    @classmethod
    def default_order_by(cls):
        return '-on_spot_creation_time'

    @property
    def render_for_month(self):
        try:
            return calendar.month_name[self.month] + ', ' + str(self.year)
        except:
            return 'N/A'

    @property
    def render_city_corporation(self):
        return self.cdc.address.geography.parent.name if self.cdc and self.cdc.address and \
                                                         self.cdc.address.geography and \
                                                         self.cdc.address.geography.parent else 'N/A'

    @classmethod
    def search_city_corporation(cls, queryset, value):
        return queryset.filter(cdc__address__geography__parent__name__icontains=value)

    @property
    def render_ward(self):
        return self.cdc.address.geography.name if self.cdc and self.cdc.address and \
                                                  self.cdc.address.geography else 'N/A'

    @classmethod
    def search_ward(cls, queryset, value):
        return queryset.filter(cdc__address__geography__name__icontains=value)

    @classmethod
    def exclude_search_fields(cls):
        return ['render_for_month']

    @classmethod
    def table_columns(cls):
        return [
            'render_code', 'cdc:CDC', 'render_ward', 'render_city_corporation', 'render_for_month',
            'date_created:Report Created', 'created_by', 'last_updated'
        ]

    @property
    def basic_info(self):
        d = OrderedDict()
        d['for_month'] = self.render_for_month
        d['CDC'] = self.cdc
        d['Remarks'] = self.remarks
        d['Location'] = self.location
        return d

    @property
    def details_config(self):
        d = OrderedDict()
        d['Basic Information'] = self.basic_info

        fvs = self.field_values.order_by('field__field_group__weight', 'field__weight').values(
            'field__field_group__name', 'field__name', 'value')

        for fv in fvs:
            if fv['field__field_group__name'] not in d.keys():
                d[fv['field__field_group__name']] = OrderedDict()
            d[fv['field__field_group__name']][fv['field__name']] = fv['value']

        return d

    def approval_level_1_action(self, action=None, *args, **kwargs):
        if action == "Approved":
            CDCMonthlyReport.objects.filter(
                year=self.year, month=self.month, cdc_id=self.cdc_id,
                type='PendingCDCMonthlyReport'
            ).update(type='ApprovedCDCMonthlyReport')
            if CDCMonthlyReport.objects.filter(cdc_id=self.cdc_id).count() == 1:
                self.is_baseline = True
                self.save()

    def final_approval_action(self, action, *args, **kwargs):
        if action == "Approved":
            _last_updated_timestamp = Clock.timestamp()
            CDCMonthlyReport.objects.filter(
                year=self.year, month=self.month, cdc_id=self.cdc_id, type='PendingCDCMonthlyReport'
            ).update(
                type='ApprovedCDCMonthlyReport',
                last_updated=_last_updated_timestamp
            )

    @classmethod
    def generate_alert_for_pending_reports(cls):
        from undp_nuprp.approvals.models import PendingCDCMonthlyReport, PendingSCGMonthlyReport
        organization_id = Organization.get_organization_from_cache().pk
        alert_time = datetime.now()
        try:
            alert_group, created = AlertGroup.objects.get_or_create(
                organization_id=organization_id,
                name='Savings and Credit Related'
            )
            model_name = CDC.__name__
            app_label = CDC._meta.app_label
            alert_group_id = alert_group.pk
            model_property = 'savings_and_credit'
            pending_cdc_reports = PendingCDCMonthlyReport.objects \
                .distinct('parent_id') \
                .order_by('parent_id', '-on_spot_creation_time')
            pending_scg_reports = PendingSCGMonthlyReport.objects \
                .distinct('parent_id') \
                .order_by('parent_id', '-on_spot_creation_time')

            pending_cdc_report_queryset = pending_cdc_reports.values('id', 'cdc')
            pending_scg_report_queryset = pending_scg_reports.values('id', 'scg__primary_group__parent')

            pending_cdc_report_dict = OrderedDict()
            for cdc_report in pending_cdc_report_queryset:
                cdc_report_id = cdc_report['id']
                cdc_id = cdc_report['cdc']
                if cdc_id not in pending_cdc_report_dict.keys():
                    pending_cdc_report_dict[cdc_id] = list()
                pending_cdc_report_dict[cdc_id].append(cdc_report_id)

            pending_scg_report_dict = OrderedDict()
            for scg_report in pending_scg_report_queryset:
                scg_report_id = scg_report['id']
                cdc_id = scg_report['scg__primary_group__parent']
                if cdc_id not in pending_scg_report_dict.keys():
                    pending_scg_report_dict[cdc_id] = list()
                pending_scg_report_dict[cdc_id].append(scg_report_id)

            cdc_ids = set(list(pending_scg_report_dict.keys()) + list(pending_cdc_report_dict.keys()))

            for cdc_id in cdc_ids:
                alert_wise_cdc_report_ids = list()
                if cdc_id in pending_cdc_report_dict.keys():
                    alert_wise_cdc_report_ids = pending_cdc_report_dict[cdc_id]

                alert_wise_scg_report_ids = list()
                if cdc_id in pending_scg_report_dict.keys():
                    alert_wise_scg_report_ids = pending_scg_report_dict[cdc_id]

                cdc_reports_count = len(alert_wise_cdc_report_ids)
                scg_reports_count = len(alert_wise_scg_report_ids)

                object_id = cdc_id
                record = SavingsAndCreditReportAlert.objects.filter(
                    alert_group_id=alert_group_id, model=model_name, app_label=app_label,
                    object_id=object_id, model_property=model_property,
                    year=alert_time.year, month=alert_time.month
                ).order_by('pk').last()
                if record is None:
                    record = SavingsAndCreditReportAlert()
                    record.organization_id = organization_id
                    record.year = alert_time.year
                    record.month = alert_time.month
                    record.day = alert_time.day
                    record.alert_group_id = alert_group_id
                    record.model = model_name
                    record.app_label = app_label
                    record.object_id = object_id
                    record.model_property = model_property
                record.body = str(scg_reports_count) + ' SCG and ' + str(cdc_reports_count) + ' CDC reports are pending'
                record.save()

                if cdc_reports_count > 0:
                    record.cdc_reports.add(*alert_wise_cdc_report_ids)
                if scg_reports_count > 0:
                    record.scg_reports.add(*alert_wise_scg_report_ids)
        except Exception as exp:
            ErrorLog.log(exp)

    @classmethod
    def get_serializer(cls):
        _ODESerializer = OrganizationDomainEntity.get_serializer()

        class Serializer(_ODESerializer):
            location = Location.get_serializer()(required=True)
            field_values = CustomFieldValue.get_serializer()(many=True, required=True)

            class Meta(_ODESerializer.Meta):
                model = cls
                fields = (
                    'id', 'tsync_id', 'type', 'year', 'month', 'cdc', 'field_values', 'location',
                    'remarks', 'date_created', 'last_updated', 'on_spot_creation_time'
                )

        return Serializer
