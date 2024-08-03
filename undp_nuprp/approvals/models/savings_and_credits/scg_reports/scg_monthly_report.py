"""
Created by tareq on 2/15/18
"""
import re
import calendar
from collections import OrderedDict

from django.db import models

from blackwidow.core.models import Location, CustomFieldValue
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators import save_audit_log
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.enums.reachout_level_enum import ReachoutLevelEnum
from blackwidow.engine.extensions import Clock
from undp_nuprp.approvals.models.savings_and_credits.base.scg_monthly_report_field import SCGMonthlyReportField
from undp_nuprp.nuprp_admin.models.infrastructure_units.savings_and_credit_group import SavingsAndCreditGroup

__author__ = 'Tareq'


@decorate(save_audit_log, expose_api('scg-monthly-report'))
class SCGMonthlyReport(OrganizationDomainEntity):
    year = models.IntegerField(default=2010)
    month = models.IntegerField(default=1)
    scg = models.ForeignKey(SavingsAndCreditGroup, null=True, on_delete=models.SET_NULL)
    field_values = models.ManyToManyField('core.CustomFieldValue')
    location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)
    remarks = models.CharField(max_length=300, null=True)
    parent = models.ForeignKey('approvals.SCGMonthlyReport', null=True)
    parent_tsync_id = models.CharField(max_length=60, null=True)
    on_spot_creation_time = models.BigIntegerField(default=0)  # when this version/object is being created
    is_baseline = models.BooleanField(default=False, editable=False)  # distinguish between baseline and monthly report

    class Meta:
        app_label = 'approvals'

    @classmethod
    def distinct_fields(cls):
        return ['parent_id']

    def save(self, *args, organization=None, **kwargs):
        super(SCGMonthlyReport, self).save(*args, organization=organization, **kwargs)
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
    def render_cdc(self):
        return self.scg.primary_group.parent if self.scg and self.scg.primary_group and self.scg.primary_group.parent \
            else 'N/A'

    @classmethod
    def search_cdc(cls, queryset, value):
        return queryset.filter(scg__primary_group__parent__name__icontains=value)


    @property
    def render_ward(self):
        return self.scg.primary_group.parent.address.geography.name \
            if self.scg and self.scg.primary_group and self.scg.primary_group.parent and \
               self.scg.primary_group.parent.address and self.scg.primary_group.parent.address.geography else 'N/A'

    @classmethod
    def search_ward(cls, queryset, value):
        return queryset.filter(scg__primary_group__parent__address__geography__name__icontains=value)


    @property
    def render_city_corporation(self):
        return self.scg.primary_group.parent.address.geography.parent.name \
            if self.scg and self.scg.primary_group and self.scg.primary_group.parent and \
               self.scg.primary_group.parent.address and self.scg.primary_group.parent.address.geography else 'N/A'


    @classmethod
    def search_city_corporation(cls, queryset, value):
        return queryset.filter(scg__primary_group__parent__address__geography__parent__name__icontains=value)

    @classmethod
    def exclude_search_fields(cls):
        return ['render_for_month']

    @classmethod
    def table_columns(cls):
        return [
            'render_code', 'scg:SCG', 'render_cdc', 'render_ward', 'render_city_corporation', 'render_for_month',
            'date_created:Report Created', 'created_by',
            'last_updated'
        ]

    @property
    def basic_info(self):
        d = OrderedDict()
        d['for_month'] = self.render_for_month
        d['SCG'] = self.scg
        d['Remarks'] = self.remarks
        d['Location'] = self.location
        return d

    @classmethod
    def get_baseline_reports(cls, scg_id):
        _base_report = SCGMonthlyReport.objects.filter(scg_id=scg_id, type='ApprovedSCGMonthlyReport',
                                                       is_baseline=True).first()
        return _base_report

    @property
    def details_config(self):
        details_dict = OrderedDict()
        details_dict['Basic Information'] = self.basic_info

        fvs = self.field_values.order_by('field__field_group__weight', 'field__weight').values(
            'field__field_group__name', 'field__name', 'value', 'field__formula', 'field__assigned_code',
            'field__weight')

        _code_wise_field_value = {}
        _group_wise_filed_value_dict = OrderedDict()

        _value_collected_from_beginning = None

        if not self.is_baseline:
            baseline_report = self.__class__.get_baseline_reports(scg_id=self.scg.id)
            _form_field = baseline_report.field_values.filter(
                field__assigned_code='002002009').first() if baseline_report else None
            _value_collected_from_beginning = _form_field.value if _form_field else None

        for fv in fvs:
            _assigned_code = fv['field__assigned_code']
            _value = fv['value']
            _value = _value_collected_from_beginning if not self.is_baseline and _assigned_code == '002002009' \
                                                        and _value_collected_from_beginning else _value
            _name = fv['field__name']
            _formula = fv['field__formula']
            _group_name = fv['field__field_group__name']
            _weight = fv['field__weight']
            _code_wise_field_value[_assigned_code] = {
                'name': _name,
                'formula': _formula,
                'value': _value,
                'group_name': fv['field__field_group__name']
            }

            if _group_name not in _group_wise_filed_value_dict.keys():
                _group_wise_filed_value_dict[_group_name] = dict()

            _group_wise_filed_value_dict[_group_name][_weight] = {
                'field_name': _name,
                'field_value': _value
            }

        _pattern = re.compile(r'@(.+?)@')

        # Calculating auto calculating formula enables fields reach out level MC

        _scg_mc_formula_fields = SCGMonthlyReportField.objects.filter(
            reachout_level=ReachoutLevelEnum.MissionControl.value).all()

        for _field in _scg_mc_formula_fields:
            _formula = _field.formula
            _assigned_codes = _pattern.findall(_formula)
            try:
                for _assigned_code in _assigned_codes:
                    _formula = _formula.replace('@' + _assigned_code + '@', str(_code_wise_field_value[_assigned_code]
                                                                                [
                                                                                    'value']) if _assigned_code in _code_wise_field_value else '0')
                _derived_value = eval(_formula)
            except:
                _derived_value = 0

            if _field.field_group.name not in _group_wise_filed_value_dict.keys():
                _group_wise_filed_value_dict[_field.field_group.name] = dict()

            _group_wise_filed_value_dict[_field.field_group.name][_field.weight] = {
                'field_name': _field.name,
                'field_value': _derived_value if type(_derived_value) != float else str(round(_derived_value, 2))
            }
            _code_wise_field_value[_field.assigned_code] = {
                'name': _field.name,
                'formula': _field.formula,
                'value': _derived_value if type(_derived_value) != float else str(round(_derived_value, 2)),
                'group_name': _field.field_group.name
            }

        for _group_name, _wieght_wise_field in _group_wise_filed_value_dict.items():
            details_dict[_group_name] = OrderedDict()
            for _w in sorted(_wieght_wise_field.keys()):
                _fname = _wieght_wise_field[_w]['field_name']
                _fval = _wieght_wise_field[_w]['field_value']
                details_dict[_group_name][_fname] = _fval

        return details_dict

    def approval_level_1_action(self, action=None, *args, **kwargs):
        from undp_nuprp.approvals.models.savings_and_credits.logs.report_log import SavingsAndCreditReportlog, \
            ActionTypeEnum
        if action == "Approved":
            SCGMonthlyReport.objects.filter(
                year=self.year, month=self.month,
                scg_id=self.scg_id, type='PendingSCGMonthlyReport'
            ).update(type='ApprovedSCGMonthlyReport')
            if SCGMonthlyReport.objects.filter(scg_id=self.scg_id).count() == 1:
                self.is_baseline = True
                self.save()

            # TODO add cumulative report
            SavingsAndCreditReportlog.create_report_log(report=self.pk, action=ActionTypeEnum.Approved.value)

    def final_approval_action(self, action, *args, **kwargs):
        from undp_nuprp.approvals.models.savings_and_credits.logs.report_log import SavingsAndCreditReportlog, \
            ActionTypeEnum
        if action == "Approved":
            _last_updated_timestamp = Clock.timestamp()
            SCGMonthlyReport.objects.filter(
                year=self.year, month=self.month,
                scg_id=self.scg_id, type='PendingSCGMonthlyReport'
            ).update(
                type='ApprovedSCGMonthlyReport',
                last_updated=_last_updated_timestamp
            )
            # TODO add cumulative report
            SavingsAndCreditReportlog.create_report_log(report=self.pk, action=ActionTypeEnum.Approved.value)

    @classmethod
    def get_serializer(cls):
        ODESerializer = OrganizationDomainEntity.get_serializer()

        class Serializer(ODESerializer):
            location = Location.get_serializer()(required=True)
            field_values = CustomFieldValue.get_serializer()(many=True, required=True)

            class Meta(ODESerializer.Meta):
                model = cls
                fields = (
                    'id', 'tsync_id', 'type', 'year', 'month', 'scg', 'field_values', 'location',
                    'remarks', 'date_created', 'last_updated', 'on_spot_creation_time'
                )

        return Serializer
