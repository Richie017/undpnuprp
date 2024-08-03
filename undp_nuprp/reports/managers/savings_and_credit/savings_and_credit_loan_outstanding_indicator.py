from collections import OrderedDict

from django.db.models.aggregates import Sum
from django.db.models.fields import IntegerField
from django.db.models.functions.base import Cast

from blackwidow.core.models.common.custom_field import CustomFieldValue
from undp_nuprp.approvals.models.savings_and_credits.cdc_reports.approved_cdc_monthly_report import \
    ApprovedCDCMonthlyReport
from undp_nuprp.reports.utils.thousand_separator import thousand_separator

__author__ = 'Shuvro'


def get_scg_member_loan_outstanding_flat_data(wards=list(), from_time=None, to_time=None):
    approved_cdc_monthly_report_domain = ApprovedCDCMonthlyReport.objects.order_by(
        'parent_id', '-on_spot_creation_time').distinct('parent_id')

    if from_time:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(date_created__gte=from_time)

    if to_time:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(date_created__lte=to_time)

    if wards:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(
            cdc__address__geography__parent__pk__in=wards)

    approved_cdc_monthly_report_ids = approved_cdc_monthly_report_domain.values_list('pk', flat=True)

    scg_loan_outstanding_queryset = CustomFieldValue.objects.filter(
        field__assigned_code='001001004', cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    outstanding_loans = scg_loan_outstanding_queryset.annotate(total=Cast('value', IntegerField())).aggregate(
        Sum('total'))

    outstanding_loan_amount = outstanding_loans['total__sum'] if outstanding_loans['total__sum'] else 0

    return '<h1 style="font-weight:bold">Cumulative value of outstanding loans (all cities)</h1><div>' \
           '<span style="font-size: 36px;">' + str(thousand_separator(outstanding_loan_amount)) + ' (BDT)</span></div>'


def get_scg_member_loan_outstanding_column_chart_data(wards=list(), from_time=None, to_time=None):
    approved_cdc_monthly_report_domain = ApprovedCDCMonthlyReport.objects.order_by(
        'parent_id', '-on_spot_creation_time').distinct('parent_id')

    if from_time:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(date_created__gte=from_time)

    if to_time:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(date_created__lte=to_time)

    if wards:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(
            cdc__address__geography__parent__pk__in=wards)

    approved_cdc_monthly_report_ids = approved_cdc_monthly_report_domain.values_list('pk', flat=True)

    scg_loan_outstanding_queryset = CustomFieldValue.objects.filter(
        field__assigned_code='001001004', cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    outstanding_loans = scg_loan_outstanding_queryset.values(
        'cdcmonthlyreport__cdc__address__geography__parent__name').annotate(
        total=Sum(Cast('value', IntegerField())))

    out_loan_amount_dict = OrderedDict()

    for cum_disbursed_loan in outstanding_loans:
        city_name = cum_disbursed_loan.get('cdcmonthlyreport__cdc__address__geography__parent__name')
        savings = cum_disbursed_loan.get('total')
        out_loan_amount_dict[city_name] = savings

    data = [
        {
            'name': 'Cumulative value of outstanding loans',
            'data': list(out_loan_amount_dict.values())
        }
    ]

    return data, list(out_loan_amount_dict.keys())




def get_scg_member_loan_outstanding_table_data(wards=list(), from_time=None, to_time=None):
    approved_cdc_monthly_report_domain = ApprovedCDCMonthlyReport.objects.order_by(
        'parent_id', '-on_spot_creation_time').distinct('parent_id')

    if from_time:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(date_created__gte=from_time)

    if to_time:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(date_created__lte=to_time)

    if wards:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(
            cdc__address__geography__parent__pk__in=wards)

    approved_cdc_monthly_report_ids = approved_cdc_monthly_report_domain.values_list('pk', flat=True)

    scg_loan_outstanding_queryset = CustomFieldValue.objects.filter(
        field__assigned_code='001001004', cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    outstanding_loans = scg_loan_outstanding_queryset.values(
        'cdcmonthlyreport__cdc__address__geography__parent__name').annotate(
        total=Sum(Cast('value', IntegerField())))

    out_loan_amount_dict = OrderedDict()

    for cum_disbursed_loan in outstanding_loans:
        city_name = cum_disbursed_loan.get('cdcmonthlyreport__cdc__address__geography__parent__name')
        savings = cum_disbursed_loan.get('total')
        out_loan_amount_dict[city_name] = savings


    response_data = list()
    response_data.append(['City/Town', 'Cumulative value of outstanding loans'])

    total = 0

    for k,v in out_loan_amount_dict.items():
        response_data.append([k, thousand_separator(round(v))])
        total += v


    response_data.append(['Total (all cities)', thousand_separator(round(total))])

    return response_data