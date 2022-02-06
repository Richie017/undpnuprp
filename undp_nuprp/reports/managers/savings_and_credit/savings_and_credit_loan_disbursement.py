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


def get_scg_member_loan_disbursement_flat_data(wards=list(), from_time=None, to_time=None):
    approved_cdc_monthly_report_domain = ApprovedCDCMonthlyReport.objects.order_by(
        'parent_id', '-on_spot_creation_time').distinct('parent_id')

    report_title = 'Cumulative value of loans disbursed (all cities)'

    if from_time:
        _from_datetime = datetime.fromtimestamp(from_time / 1000)
        _from_year = _from_datetime.year
        _from_month = _from_datetime.month
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(year__gte=_from_year,
                                                                                       month__gte=_from_month)
        report_title = 'Value of loans disbursed during the reporting period (all cities)'

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

    scg_disbursed_loan_queryset = CustomFieldValue.objects.filter(
        field__assigned_code='001001007', cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    disbursed_loans = scg_disbursed_loan_queryset.annotate(total=Cast('value', FloatField())).aggregate(Sum('total'))

    disbursed_loan_amount = disbursed_loans['total__sum'] if disbursed_loans['total__sum'] else 0

    return '<h1 style="font-weight:bold">{title}</h1><div>'.format(title=report_title) + \
           '<span style="font-size: 36px;">' + str(
        thousand_separator(round(disbursed_loan_amount))) + ' (BDT)</span></div>'


def get_scg_member_loan_disbursement_column_chart_data(wards=list(), from_time=None, to_time=None):
    approved_cdc_monthly_report_domain = ApprovedCDCMonthlyReport.objects.order_by(
        'parent_id', '-on_spot_creation_time').distinct('parent_id')

    report_name = 'Cumulative value of disbursed Loans'

    if from_time:
        _from_datetime = datetime.fromtimestamp(from_time / 1000)
        _from_year = _from_datetime.year
        _from_month = _from_datetime.month
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(year__gte=_from_year,
                                                                                       month__gte=_from_month)
        report_name = 'value of disbursed Loans'

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

    scg_disbursed_loan_queryset = CustomFieldValue.objects.filter(
        field__assigned_code='001001007', cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    cum_disbursed_loans = scg_disbursed_loan_queryset.values(
        'cdcmonthlyreport__cdc__address__geography__parent__name').annotate(
        total=Sum(Cast('value', FloatField())))

    cumulative_saving_balance_dict = OrderedDict()

    for cum_disbursed_loan in cum_disbursed_loans:
        city_name = cum_disbursed_loan.get('cdcmonthlyreport__cdc__address__geography__parent__name')
        savings = cum_disbursed_loan.get('total')
        cumulative_saving_balance_dict[city_name] = savings

    data = [
        {
            'name': report_name,
            'data': list(cumulative_saving_balance_dict.values())
        }
    ]

    return data, list(cumulative_saving_balance_dict.keys())





def get_scg_member_loan_disbursement_table_data(wards=list(), from_time=None, to_time=None):
    approved_cdc_monthly_report_domain = ApprovedCDCMonthlyReport.objects.order_by(
        'parent_id', '-on_spot_creation_time').distinct('parent_id')

    report_name = 'Cumulative value of disbursed Loans'

    if from_time:
        _from_datetime = datetime.fromtimestamp(from_time / 1000)
        _from_year = _from_datetime.year
        _from_month = _from_datetime.month
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(year__gte=_from_year,
                                                                                       month__gte=_from_month)
        report_name = 'value of disbursed Loans'

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

    scg_disbursed_loan_queryset = CustomFieldValue.objects.filter(
        field__assigned_code='001001007', cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    cum_disbursed_loans = scg_disbursed_loan_queryset.values(
        'cdcmonthlyreport__cdc__address__geography__parent__name').annotate(
        total=Sum(Cast('value', FloatField())))

    cumulative_saving_balance_dict = OrderedDict()

    for cum_disbursed_loan in cum_disbursed_loans:
        city_name = cum_disbursed_loan.get('cdcmonthlyreport__cdc__address__geography__parent__name')
        savings = cum_disbursed_loan.get('total')
        cumulative_saving_balance_dict[city_name] = savings


    response_data = list()
    total = 0

    response_data.append(['City/Town', 'Value of disbursed loans'])

    for k, v in cumulative_saving_balance_dict.items():
        response_data.append([k, thousand_separator(round(v))])
        total += v

    response_data.append(['Total (all cities)', thousand_separator(round(total))])

    return response_data


