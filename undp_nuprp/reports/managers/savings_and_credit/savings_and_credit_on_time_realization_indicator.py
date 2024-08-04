from collections import OrderedDict
from datetime import datetime

from django.db.models.aggregates import Sum
from django.db.models.fields import IntegerField, FloatField
from django.db.models.functions import Cast

from blackwidow.core.models.common.custom_field import CustomFieldValue
from undp_nuprp.approvals.models.savings_and_credits.scg_reports.approved_scg_monthly_report import \
    ApprovedSCGMonthlyReport

__author__ = 'Shuvro'

#002002005 - Total collected current loan (Principal + Interest) for the reporting month
#002002004 - Total targeted receivable current loan (Principal + Interest) for the reporting month
#002002007 - Value of total loan collected (Principal+ Interest) of Overdue + Advances for the reporting month


def get_scg_member_on_time_realization_flat_data(wards=list(), from_time=None, to_time=None):
    approved_scg_monthly_report_domain = ApprovedSCGMonthlyReport.objects.order_by(
        'parent_id', '-on_spot_creation_time').distinct('parent_id')

    if from_time:
        _from_datetime = datetime.fromtimestamp(from_time / 1000)
        _from_year = _from_datetime.year
        _from_month = _from_datetime.month
        approved_scg_monthly_report_domain = approved_scg_monthly_report_domain.filter(year__gte=_from_year,
                                                                                       month__gte=_from_month)

    if to_time:
        _to_datetime = datetime.fromtimestamp(to_time / 1000)
        _to_year = _to_datetime.year
        _to_month = _to_datetime.month
        approved_scg_monthly_report_domain = approved_scg_monthly_report_domain.filter(year__lte=_to_year,
                                                                                       month__lte=_to_month)

    if wards:
        approved_scg_monthly_report_domain = approved_scg_monthly_report_domain.filter(
            cdc__address__geography__parent__pk__in=wards)

    approved_scg_monthly_report_ids = approved_scg_monthly_report_domain.values_list('pk', flat=True)

    scg_curr_loan_collection_queryset = CustomFieldValue.objects.filter(
        field__assigned_code='002002005', scgmonthlyreport__pk__in=approved_scg_monthly_report_ids
    )

    scg_loan_collection_queryset = CustomFieldValue.objects.filter(
        field__assigned_code='002002007', scgmonthlyreport__pk__in=approved_scg_monthly_report_ids
    )

    scg_loan_receivable_target_queryset = CustomFieldValue.objects.filter(
        field__assigned_code='002002004', scgmonthlyreport__pk__in=approved_scg_monthly_report_ids
    )

    scg_curr_loan_collection_values = scg_curr_loan_collection_queryset.annotate(
        total=Cast('value', IntegerField())).aggregate(Sum('total'))

    scg_loan_collection_values = scg_loan_collection_queryset.annotate(total=Cast('value', FloatField())).aggregate(
        Sum('total'))

    scg_loan_receivable_target_values = scg_loan_receivable_target_queryset.annotate(
        total=Cast('value', IntegerField())).aggregate(Sum('total'))

    scg_curr_loan_collection_amount = scg_curr_loan_collection_values['total__sum'] if scg_curr_loan_collection_values[
        'total__sum'] else 0
    scg_loan_collection_amount = scg_loan_collection_values['total__sum'] if scg_loan_collection_values[
        'total__sum'] else 0
    scg_loan_receivable_target_amount = scg_loan_receivable_target_values['total__sum'] if \
        scg_loan_receivable_target_values[
            'total__sum'] else 0

    on_time_realization = (scg_curr_loan_collection_amount - scg_loan_collection_amount) / \
                           scg_loan_receivable_target_amount if scg_loan_receivable_target_amount > 0 else 0

    return '<h1 style="font-weight:bold">Ratio of on-time realization (all cities)</h1><div>' \
           '<span style="font-size: 36px;">' + str(round(on_time_realization * 100, 2)) + '%</span></div>'


def get_scg_member_on_time_realization_column_chart_data(wards=list(), from_time=None, to_time=None):
    approved_scg_monthly_report_domain = ApprovedSCGMonthlyReport.objects.order_by(
        'parent_id', '-on_spot_creation_time').distinct('parent_id')

    if from_time:
        _from_datetime = datetime.fromtimestamp(from_time / 1000)
        _from_year = _from_datetime.year
        _from_month = _from_datetime.month
        approved_scg_monthly_report_domain = approved_scg_monthly_report_domain.filter(year__gte=_from_year,
                                                                                       month__gte=_from_month)

    if to_time:
        _to_datetime = datetime.fromtimestamp(to_time / 1000)
        _to_year = _to_datetime.year
        _to_month = _to_datetime.month
        approved_scg_monthly_report_domain = approved_scg_monthly_report_domain.filter(year__lte=_to_year,
                                                                                       month__lte=_to_month)

    if wards:
        approved_scg_monthly_report_domain = approved_scg_monthly_report_domain.filter(
            scgmonthlyreport__scg__address__geography__parent__pk__in=wards)

    approved_scg_monthly_report_ids = approved_scg_monthly_report_domain.values_list('pk', flat=True)

    scg_loans = CustomFieldValue.objects.filter(
        field__assigned_code__in=['002002005', '002002007', '002002004'],
        scgmonthlyreport__pk__in=approved_scg_monthly_report_ids
    ).values('scgmonthlyreport__scg__address__geography__parent__name', 'field__assigned_code', 'value')

    on_time_realization_dict = OrderedDict()

    for scg_loan in scg_loans:
        city_name = scg_loan['scgmonthlyreport__scg__address__geography__parent__name']
        field_code = scg_loan['field__assigned_code']
        field_value = scg_loan['value']
        if scg_loan['scgmonthlyreport__scg__address__geography__parent__name'] not in on_time_realization_dict:
            on_time_realization_dict[city_name] = {
                '002002005': 0, '002002007': 0, '002002004': 0
            }
        on_time_realization_dict[city_name][field_code] += float(field_value)

    on_time_real_values = []

    for on_time_realization in on_time_realization_dict.values():
        ratio = (on_time_realization['002002005'] - on_time_realization['002002007']) / on_time_realization[
            '002002004'] if on_time_realization['002002004'] > 0 else 0
        on_time_real_values.append(round(ratio * 100, 2))

    data = [
        {
            'name': 'Ratio of on-time realization',
            'data': on_time_real_values
        }
    ]

    return data, list(on_time_realization_dict.keys())




def get_scg_member_on_time_realization_table_data(wards=list(), from_time=None, to_time=None):
    approved_scg_monthly_report_domain = ApprovedSCGMonthlyReport.objects.order_by(
        'parent_id', '-on_spot_creation_time').distinct('parent_id')

    if from_time:
        _from_datetime = datetime.fromtimestamp(from_time / 1000)
        _from_year = _from_datetime.year
        _from_month = _from_datetime.month
        approved_scg_monthly_report_domain = approved_scg_monthly_report_domain.filter(year__gte=_from_year,
                                                                                       month__gte=_from_month)

    if to_time:
        _to_datetime = datetime.fromtimestamp(to_time / 1000)
        _to_year = _to_datetime.year
        _to_month = _to_datetime.month
        approved_scg_monthly_report_domain = approved_scg_monthly_report_domain.filter(year__lte=_to_year,
                                                                                       month__lte=_to_month)

    if wards:
        approved_scg_monthly_report_domain = approved_scg_monthly_report_domain.filter(
            scgmonthlyreport__scg__address__geography__parent__pk__in=wards)

    approved_scg_monthly_report_ids = approved_scg_monthly_report_domain.values_list('pk', flat=True)

    scg_loans = CustomFieldValue.objects.filter(
        field__assigned_code__in=['002002005', '002002007', '002002004'],
        scgmonthlyreport__pk__in=approved_scg_monthly_report_ids
    ).values('scgmonthlyreport__scg__address__geography__parent__name', 'field__assigned_code', 'value')

    on_time_realization_dict = OrderedDict()

    for scg_loan in scg_loans:
        city_name = scg_loan['scgmonthlyreport__scg__address__geography__parent__name']
        field_code = scg_loan['field__assigned_code']
        field_value = scg_loan['value']
        if scg_loan['scgmonthlyreport__scg__address__geography__parent__name'] not in on_time_realization_dict:
            on_time_realization_dict[city_name] = {
                '002002005': 0, '002002007': 0, '002002004': 0
            }
        on_time_realization_dict[city_name][field_code] += float(field_value)


    response_data = []
    response_data.append(['City/Town', 'Ratio of on-time realization'])

    _total_value_2005 = 0
    _total_value_2007 = 0
    _total_value_2004 = 0

    for city_name in on_time_realization_dict.keys():
        _value_2005 = on_time_realization_dict[city_name]['002002005']
        _value_2007 = on_time_realization_dict[city_name]['002002007']
        _value_2004 = on_time_realization_dict[city_name]['002002004']


        ratio = (_value_2005 - _value_2007)/_value_2004 if _value_2004 > 0 else 0
        response_data.append([city_name, round(ratio * 100, 2)])

        _total_value_2005 += _value_2005
        _total_value_2007 += _value_2007
        _total_value_2004 += _value_2004


    _total_ratio = (_total_value_2005 - _total_value_2007) / _total_value_2004 if _total_value_2004 > 0 else 0
    response_data.append(["Total (all cities)",round(_total_ratio * 100, 2)])

    return response_data