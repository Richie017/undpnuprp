from collections import OrderedDict
from datetime import datetime

from django.db.models.aggregates import Sum
from django.db.models.fields import FloatField
from django.db.models.functions.base import Cast

from blackwidow.core.models.common.custom_field import CustomFieldValue
from undp_nuprp.approvals.models.savings_and_credits.cdc_reports.approved_cdc_monthly_report import \
    ApprovedCDCMonthlyReport
from undp_nuprp.reports.utils.thousand_separator import thousand_separator


def get_scg_member_saving_and_credit_savings_indicator_flat_data(wards=list(), from_time=None, to_time=None):
    approved_cdc_monthly_report_domain = ApprovedCDCMonthlyReport.objects.order_by(
        'parent_id', '-on_spot_creation_time').distinct('parent_id')

    if from_time:
        _from_datetime = datetime.fromtimestamp(from_time / 1000)
        _from_year = _from_datetime.year
        _from_month = _from_datetime.month
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(year__gte=_from_year,
                                                                                       month__gte=_from_month)

    if to_time:
        _to_datetime = datetime.fromtimestamp(to_time / 1000)
        _to_year = _to_datetime.year
        _to_month = _to_datetime.month
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(year__lte=_to_year,
                                                                                       month__lte=_to_month)

    if wards:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(
            cdc__address__geography__parent__pk__in=wards)
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(
            cdc__address__geography__parent__pk__in=wards)

    approved_cdc_monthly_report_ids = approved_cdc_monthly_report_domain.values_list('pk', flat=True)

    scg_savings_queryset = CustomFieldValue.objects.filter(
        field__assigned_code='001005002', cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    scg_withdrawn_savings_queryset = CustomFieldValue.objects.filter(
        field__assigned_code='001005004', cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    scg_savings = scg_savings_queryset.annotate(total=Cast('value', FloatField())).aggregate(Sum('total'))['total__sum']
    scg_withdrawn_savings = scg_withdrawn_savings_queryset.annotate(total=Cast('value', FloatField())).aggregate(
        Sum('total'))['total__sum']

    scg_savings = scg_savings if scg_savings else 0
    scg_withdrawn_savings = scg_withdrawn_savings if scg_withdrawn_savings else 0

    value_of_saving_balance = scg_savings - scg_withdrawn_savings

    return '<h1 style="font-weight:bold">Value of savings balance for the reporting period' \
           ' (all cities)</h1><div><span style="font-size: 36px;">' \
           + str(thousand_separator(round(value_of_saving_balance))) + ' (BDT)</span></div>'


def get_scg_member_saving_and_credit_savings_indicator_chart_data(wards=list(), from_time=None, to_time=None):
    approved_cdc_monthly_report_domain = ApprovedCDCMonthlyReport.objects.order_by(
        'parent_id', '-on_spot_creation_time').distinct('parent_id')

    if from_time:
        _from_datetime = datetime.fromtimestamp(from_time / 1000)
        _from_year = _from_datetime.year
        _from_month = _from_datetime.month
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(year__gte=_from_year,
                                                                                       month__gte=_from_month)

    if to_time:
        _to_datetime = datetime.fromtimestamp(to_time / 1000)
        _to_year = _to_datetime.year
        _to_month = _to_datetime.month
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(year__lte=_to_year,
                                                                                       month__lte=_to_month)

    if wards:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(
            cdc__address__geography__parent__pk__in=wards)
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(
            cdc__address__geography__parent__pk__in=wards)

    approved_cdc_monthly_report_ids = approved_cdc_monthly_report_domain.values_list('pk', flat=True)

    scg_savings_queryset = CustomFieldValue.objects.filter(
        field__assigned_code='001005002', cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    scg_withdrawn_savings_queryset = CustomFieldValue.objects.filter(
        field__assigned_code='001005004', cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    scg_savings = scg_savings_queryset.values('cdcmonthlyreport__cdc__address__geography__parent__name').annotate(
        total=Sum(Cast('value', FloatField())))

    scg_withdrawn_savings = scg_withdrawn_savings_queryset.values(
        'cdcmonthlyreport__cdc__address__geography__parent__name').annotate(
        total=Sum(Cast('value', FloatField())))

    scg_savings_minus_withdrl_dict = OrderedDict()

    for scg_saving in scg_savings:
        city_name = scg_saving.get('cdcmonthlyreport__cdc__address__geography__parent__name')
        savings = scg_saving.get('total')
        scg_savings_minus_withdrl_dict[city_name] = savings

    for scg_withdrawn_saving in scg_withdrawn_savings:
        city_name = scg_withdrawn_saving.get('cdcmonthlyreport__cdc__address__geography__parent__name')
        savings = scg_withdrawn_saving.get('total')
        if city_name in scg_savings_minus_withdrl_dict:
            scg_savings_minus_withdrl_dict[city_name] -= savings

    data = [
        {
            'name': 'Savings balance',
            'data': list(scg_savings_minus_withdrl_dict.values())
        }
    ]

    return data, list(scg_savings_minus_withdrl_dict.keys())




def get_scg_member_saving_and_credit_savings_indicator_table_data(wards=list(), from_time=None, to_time=None):
    approved_cdc_monthly_report_domain = ApprovedCDCMonthlyReport.objects.order_by(
        'parent_id', '-on_spot_creation_time').distinct('parent_id')

    if from_time:
        _from_datetime = datetime.fromtimestamp(from_time / 1000)
        _from_year = _from_datetime.year
        _from_month = _from_datetime.month
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(year__gte=_from_year,
                                                                                       month__gte=_from_month)

    if to_time:
        _to_datetime = datetime.fromtimestamp(to_time / 1000)
        _to_year = _to_datetime.year
        _to_month = _to_datetime.month
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(year__lte=_to_year,
                                                                                       month__lte=_to_month)

    if wards:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(
            cdc__address__geography__parent__pk__in=wards)
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(
            cdc__address__geography__parent__pk__in=wards)

    approved_cdc_monthly_report_ids = approved_cdc_monthly_report_domain.values_list('pk', flat=True)

    scg_savings_queryset = CustomFieldValue.objects.filter(
        field__assigned_code='001005002', cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    scg_withdrawn_savings_queryset = CustomFieldValue.objects.filter(
        field__assigned_code='001005004', cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    scg_savings = scg_savings_queryset.values('cdcmonthlyreport__cdc__address__geography__parent__name').annotate(
        total=Sum(Cast('value', FloatField())))

    scg_withdrawn_savings = scg_withdrawn_savings_queryset.values(
        'cdcmonthlyreport__cdc__address__geography__parent__name').annotate(
        total=Sum(Cast('value', FloatField())))

    scg_savings_minus_withdrl_dict = OrderedDict()

    for scg_saving in scg_savings:
        city_name = scg_saving.get('cdcmonthlyreport__cdc__address__geography__parent__name')
        savings = scg_saving.get('total')
        scg_savings_minus_withdrl_dict[city_name] = savings

    for scg_withdrawn_saving in scg_withdrawn_savings:
        city_name = scg_withdrawn_saving.get('cdcmonthlyreport__cdc__address__geography__parent__name')
        savings = scg_withdrawn_saving.get('total')
        if city_name in scg_savings_minus_withdrl_dict:
            scg_savings_minus_withdrl_dict[city_name] -= savings

    response_data = list()
    total = 0
    response_data.append(['City/Town', 'Savings balance'])

    for k, v in scg_savings_minus_withdrl_dict.items():
        response_data.append([k, thousand_separator(round(v))])
        total += v

    response_data.append(['Total (all cities)', thousand_separator(round(total))])

    return response_data

