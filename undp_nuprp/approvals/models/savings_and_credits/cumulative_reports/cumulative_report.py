import calendar
import re
from collections import OrderedDict
from datetime import datetime

from django.db import models

from blackwidow.core.models import Organization, CustomFieldValue, ErrorLog
from blackwidow.core.models.common.location import Location
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.field_type_enum import FieldTypesEnum
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.approvals.models.savings_and_credits.base.cumulative_report_field import CumulativeReportField
from undp_nuprp.approvals.models.savings_and_credits.cdc_reports.approved_cdc_monthly_report import \
    ApprovedCDCMonthlyReport
from undp_nuprp.approvals.models.savings_and_credits.scg_reports.approved_scg_monthly_report import \
    ApprovedSCGMonthlyReport
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc import CDC
from undp_nuprp.nuprp_admin.models.infrastructure_units.savings_and_credit_group import SavingsAndCreditGroup
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group_member import PrimaryGroupMember

__author__ = 'Ziaul Haque'


@decorate(is_object_context,
          route(route='cumulative-reports', group='Savings & Credit Reports', module=ModuleEnum.Execute,
                display_name='Cumulative Reports', group_order=1, item_order=5))
class CumulativeReport(OrganizationDomainEntity):
    year = models.IntegerField(default=2010)
    month = models.IntegerField(default=1)
    cdc = models.ForeignKey(CDC, null=True, on_delete=models.SET_NULL)
    total_scg = models.IntegerField(default=0)
    total_scg_member = models.IntegerField(default=0)
    field_values = models.ManyToManyField('core.CustomFieldValue')
    location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)
    remarks = models.CharField(max_length=300, null=True)
    parent = models.ForeignKey('approvals.CumulativeReport', null=True)
    parent_tsync_id = models.CharField(max_length=60, null=True)

    class Meta:
        app_label = 'approvals'

    @property
    def render_for_month(self):
        try:
            return calendar.month_name[self.month] + ', ' + str(self.year)
        except:
            return 'N/A'

    @classmethod
    def calculate_total_scg(cls, cdc_id=None):
        total_scg = 0
        if cdc_id:
            total_scg = SavingsAndCreditGroup.objects.filter(primary_group__parent_id=cdc_id).count()
        return total_scg

    @classmethod
    def calculate_total_scg_member(cls, cdc_id=None):
        total_scg_member = 0
        if cdc_id:
            total_scg_member = PrimaryGroupMember.objects.filter(
                savingsandcreditgroup__primary_group__parent_id=cdc_id).count()
        return total_scg_member

    @classmethod
    def generate_cumulative_report(cls, year=None, month=None):
        _today = datetime.now()
        if year is None:
            year = _today.year
        if month is None:
            month = _today.month

        cdc_queryset = CDC.objects.all()
        for cdc in cdc_queryset:
            cdc_id = cdc.id
            cls.generate_cumulative_report_for_given_month(cdc_id=cdc_id, year=year, month=month)
            print("Generating Cumulative Report for => Month: %s, Year: %s, CDC: %s" % (str(year), str(month), str(cdc_id)))

    @classmethod
    def generate_cumulative_report_for_given_month(cls, cdc_id=None, year=None, month=None):
        organization = Organization.objects.first()
        report_object, created = cls.objects.get_or_create(
            cdc_id=cdc_id, year=year, month=month, organization_id=organization.id
        )
        report_object.total_scg = cls.calculate_total_scg(cdc_id=cdc_id)
        report_object.total_scg_member = cls.calculate_total_scg_member(cdc_id=cdc_id)
        report_object.save()

        cumulative_report_fields = CumulativeReportField.objects\
            .filter(field_type=FieldTypesEnum.Calculated_Field.value)\
            .order_by('assigned_code')
        for _field in cumulative_report_fields:
            _formula = _field.formula
            result = cls.calculate_field_value(
                formula=_formula, report_object=report_object, cdc_id=cdc_id, year=year, month=month
            )
            field_value_object = CustomFieldValue.objects.create(field=_field, value=result)
            report_object.field_values.add(field_value_object)

    @classmethod
    def last_day_of_month(cls, any_day):
        import datetime
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
        return next_month - datetime.timedelta(days=next_month.day)

    @classmethod
    def calculate_field_value(cls, formula=None, report_object=None, cdc_id=None, year=None, month=None):
        _calculated_value = 0
        _pattern = re.compile(r'@(.+?)@')

        _end_timestamp = cls.last_day_of_month(
            datetime.now().replace(year=year, month=month)
        ).replace(hour=23, minute=59, second=59).timestamp() * 1000

        # filtering on queryset: start
        approved_cdc_report_ids = ApprovedCDCMonthlyReport.objects.filter(
            cdc_id=cdc_id, on_spot_creation_time__lte=_end_timestamp
        ).distinct('parent').order_by('parent', '-on_spot_creation_time').values_list('id', flat=True)

        approved_scg_reports_ids = ApprovedSCGMonthlyReport.objects.filter(
            scg__primary_group__parent_id=cdc_id, on_spot_creation_time__lte=_end_timestamp
        ).distinct('parent').order_by('parent', '-on_spot_creation_time').values_list('id', flat=True)

        field_value_ids = list(CustomFieldValue.objects.filter(
            cdcmonthlyreport__pk__in=approved_cdc_report_ids
        ).values_list('id', flat=True))

        field_value_ids += list(CustomFieldValue.objects.filter(
            scgmonthlyreport__pk__in=approved_scg_reports_ids
        ).values_list('id', flat=True))

        field_value_queryset = CustomFieldValue.objects.filter(pk__in=field_value_ids)
        # filtering on queryset: end

        # sum of all field values
        if formula.startswith('SUM'):
            _assigned_code = _pattern.findall(formula)[0]
            values_list = list(field_value_queryset.filter(
                field__assigned_code=_assigned_code
            ).values_list('value', flat=True))
            for _value in values_list:
                try:
                    _calculated_value += float(_value)
                except:
                    pass

        elif formula.startswith('LATEST'):
            _assigned_code = _pattern.findall(formula)[0]
            _latest_entry = field_value_queryset.filter(
                field__assigned_code=_assigned_code
            ).order_by('-last_updated').first()
            if _latest_entry and _latest_entry.value:
                try:
                    _calculated_value = float(_latest_entry.value)
                except:
                    pass
        else:
            _assigned_codes = _pattern.findall(formula)
            for _assigned_code in _assigned_codes:
                _latest_entry = report_object.field_values.filter(
                    field__assigned_code=_assigned_code
                ).order_by('-last_updated').first()
                _value = 0
                if _latest_entry and _latest_entry.value:
                    _value = _latest_entry.value
                formula = formula.replace('@' + _assigned_code + '@', str(_value))
            try:
                _calculated_value = eval(formula)
            except Exception as exp:
                ErrorLog.log(exp)
        return _calculated_value

    @classmethod
    def table_columns(cls):
        return [
            'render_code', 'cdc:CDC', 'render_for_month', 'date_created:Report Created', 'created_by', 'last_updated'
        ]

    @property
    def basic_info(self):
        details = OrderedDict()
        details['for_month'] = self.render_for_month
        details['CDC'] = self.cdc
        details['Total SCG'] = self.total_scg
        details['Total SCG Member'] = self.total_scg_member
        return details

    @property
    def details_config(self):
        details = OrderedDict()
        details['Basic Information'] = self.basic_info

        fvs = self.field_values \
            .order_by('field__field_group__weight', 'field__weight') \
            .values('field__field_group__name', 'field__name', 'value')

        for fv in fvs:
            if fv['field__field_group__name'] not in details.keys():
                details[fv['field__field_group__name']] = OrderedDict()
            details[fv['field__field_group__name']][fv['field__name']] = fv['value']

        return details
