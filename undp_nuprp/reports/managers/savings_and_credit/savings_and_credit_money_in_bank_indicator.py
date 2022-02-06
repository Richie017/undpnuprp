from collections import OrderedDict
from datetime import datetime

from django.db.models.aggregates import Sum
from django.db.models.fields import FloatField
from django.db.models.functions.base import Cast

from blackwidow.core.models.common.custom_field import CustomFieldValue
from undp_nuprp.approvals.models.savings_and_credits.cdc_reports.approved_cdc_monthly_report import \
    ApprovedCDCMonthlyReport
from undp_nuprp.reports.utils.thousand_separator import thousand_separator

__author__ = 'Shuvro'


def get_scg_member_money_in_bank_indicator_flat_data(wards=list(), from_time=None, to_time=None):
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

    approved_cdc_monthly_report_ids = approved_cdc_monthly_report_domain.values_list('pk', flat=True)

    scg_money_in_bank_queryset = CustomFieldValue.objects.filter(
        field__assigned_code='001003001', cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    scg_money_in_bank_amount = scg_money_in_bank_queryset.annotate(total_amount=Cast('value', FloatField())).aggregate(
        Sum('total_amount'))

    scg_money_in_bank_amount = scg_money_in_bank_amount['total_amount__sum'] if scg_money_in_bank_amount[
        'total_amount__sum'] else 0

    return '<h1 style="font-weight:bold">Value of money in the bank during reporting month (all cities)</h1><div>' \
           '<span style="font-size: 36px;">' + str(
        thousand_separator(round(scg_money_in_bank_amount))) + ' (BDT)</span></div>'


def get_scg_member_money_in_bank_indicator_column_chart_data(wards=list(), from_time=None, to_time=None):
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

    approved_cdc_monthly_report_ids = approved_cdc_monthly_report_domain.values_list('pk', flat=True)

    scg_money_in_bank_by_city_queryset = CustomFieldValue.objects.values(
        'cdcmonthlyreport__cdc__address__geography__parent__name').filter(
        field__assigned_code='001003001', cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    scg_money_in_bank_by_cities = scg_money_in_bank_by_city_queryset.annotate(total=Sum(Cast('value', FloatField())))

    scg_money_in_bank_by_cities_dict = OrderedDict()

    for scg_money_in_bank_by_city in scg_money_in_bank_by_cities:
        city = scg_money_in_bank_by_city['cdcmonthlyreport__cdc__address__geography__parent__name']
        money_in_bank = scg_money_in_bank_by_city['total']
        scg_money_in_bank_by_cities_dict[city] = money_in_bank

    data = [
        {
            'name': 'Money in the bank during reporting month',
            'data': list(scg_money_in_bank_by_cities_dict.values())
        }
    ]

    return data, list(scg_money_in_bank_by_cities_dict.keys())



def get_scg_member_money_in_bank_indicator_table_data(wards=list(), from_time=None, to_time=None):
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

    approved_cdc_monthly_report_ids = approved_cdc_monthly_report_domain.values_list('pk', flat=True)

    scg_money_in_bank_by_city_queryset = CustomFieldValue.objects.values(
        'cdcmonthlyreport__cdc__address__geography__parent__name').filter(
        field__assigned_code='001003001', cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    scg_money_in_bank_by_cities = scg_money_in_bank_by_city_queryset.annotate(total=Sum(Cast('value', FloatField())))

    scg_money_in_bank_by_cities_dict = OrderedDict()

    for scg_money_in_bank_by_city in scg_money_in_bank_by_cities:
        city = scg_money_in_bank_by_city['cdcmonthlyreport__cdc__address__geography__parent__name']
        money_in_bank = scg_money_in_bank_by_city['total']
        scg_money_in_bank_by_cities_dict[city] = money_in_bank

    response_data = list()
    response_data.append(['City/Town', 'Money in the bank'])

    total = 0

    for k, v in scg_money_in_bank_by_cities_dict.items():
        response_data.append([k, thousand_separator(round(v))])
        total += v

    response_data.append(['Total (all cities)', thousand_separator(round(total))])

    return response_data