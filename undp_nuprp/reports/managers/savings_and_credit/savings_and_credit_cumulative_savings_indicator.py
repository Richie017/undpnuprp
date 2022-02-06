from collections import OrderedDict

from django.db.models.aggregates import Sum
from django.db.models.fields import FloatField
from django.db.models.functions.base import Cast

from blackwidow.core.models.common.custom_field import CustomFieldValue
from undp_nuprp.approvals.models.savings_and_credits.cdc_reports.approved_cdc_monthly_report import \
    ApprovedCDCMonthlyReport
from undp_nuprp.reports.utils.thousand_separator import thousand_separator

__author__ = 'Shuvro'


def get_scg_member_cumulative_savings_indicator_flat_data(wards=list(), from_time=None, to_time=None):
    approved_cdc_monthly_report_domain = ApprovedCDCMonthlyReport.objects.order_by(
        'parent_id', '-on_spot_creation_time').distinct('parent_id')

    if from_time:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(
            date_created__gte=from_time - 1000)
    if to_time:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(date_created__lte=to_time + 1000)

    if wards:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(
            cdc__address__geography__parent__pk__in=wards)
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(
            cdc__address__geography__parent__pk__in=wards)

    approved_cdc_monthly_report_ids = approved_cdc_monthly_report_domain.values_list('pk', flat=True)

    scg_savings_queryset = CustomFieldValue.objects.filter(
        field__assigned_code='001005002', cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    scg_savings = scg_savings_queryset.annotate(total=Cast('value', FloatField())).aggregate(Sum('total'))

    cumulative_saving_balance = scg_savings['total__sum']

    return '<h1 style="font-weight:bold">Cumulative value of total savings (all cities)</h1><div>' \
           '<span style="font-size: 36px;">' \
           + str(thousand_separator(round(cumulative_saving_balance))) + ' (BDT)</span></div>'


def get_scg_member_cumulative_savings_indicator_column_chart_data(wards=list(), from_time=None, to_time=None):
    approved_cdc_monthly_report_domain = ApprovedCDCMonthlyReport.objects.order_by(
        'parent_id', '-on_spot_creation_time').distinct('parent_id')

    if from_time:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(
            date_created__gte=from_time - 1000)
    if to_time:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(date_created__lte=to_time + 1000)

    if wards:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(
            cdc__address__geography__parent__pk__in=wards)
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(
            cdc__address__geography__parent__pk__in=wards)

    approved_cdc_monthly_report_ids = approved_cdc_monthly_report_domain.values_list('pk', flat=True)

    scg_savings_queryset = CustomFieldValue.objects.filter(
        field__assigned_code='001005002', cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    scg_savings = scg_savings_queryset.values('cdcmonthlyreport__cdc__address__geography__parent__name').annotate(
        total=Sum(Cast('value', FloatField())))

    cumulative_saving_balance_dict = OrderedDict()

    for scg_saving in scg_savings:
        city_name = scg_saving.get('cdcmonthlyreport__cdc__address__geography__parent__name')
        savings = scg_saving.get('total')
        cumulative_saving_balance_dict[city_name] = savings

    data = [
        {
            'name': 'Cumulative savings balance',
            'data': list(cumulative_saving_balance_dict.values())
        }
    ]

    return data, list(cumulative_saving_balance_dict.keys())




def get_scg_member_cumulative_savings_indicator_table_data(wards=list(), from_time=None, to_time=None):
    approved_cdc_monthly_report_domain = ApprovedCDCMonthlyReport.objects.order_by(
        'parent_id', '-on_spot_creation_time').distinct('parent_id')

    if from_time:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(
            date_created__gte=from_time - 1000)
    if to_time:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(date_created__lte=to_time + 1000)

    if wards:
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(
            cdc__address__geography__parent__pk__in=wards)
        approved_cdc_monthly_report_domain = approved_cdc_monthly_report_domain.filter(
            cdc__address__geography__parent__pk__in=wards)

    approved_cdc_monthly_report_ids = approved_cdc_monthly_report_domain.values_list('pk', flat=True)

    scg_savings_queryset = CustomFieldValue.objects.filter(
        field__assigned_code='001005002', cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    scg_savings = scg_savings_queryset.values('cdcmonthlyreport__cdc__address__geography__parent__name').annotate(
        total=Sum(Cast('value', FloatField())))

    cumulative_saving_balance_dict = OrderedDict()

    for scg_saving in scg_savings:
        city_name = scg_saving.get('cdcmonthlyreport__cdc__address__geography__parent__name')
        savings = scg_saving.get('total')
        cumulative_saving_balance_dict[city_name] = savings


    response_data = list()
    total = 0

    response_data.append(['City/Town', 'Cumulative savings balance'])

    for k, v in cumulative_saving_balance_dict.items():
        response_data.append([k, thousand_separator(round(v))])
        total += v

    response_data.append(['Total (all cities)', thousand_separator(round(total))])

    return response_data



