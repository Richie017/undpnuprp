from collections import OrderedDict

from django.db.models.aggregates import Sum
from django.db.models.fields import FloatField
from django.db.models.functions.base import Cast

from blackwidow.core.models.common.custom_field import CustomFieldValue
from undp_nuprp.approvals.models.savings_and_credits.cdc_reports.approved_cdc_monthly_report import \
    ApprovedCDCMonthlyReport
from undp_nuprp.reports.utils.thousand_separator import thousand_separator

__author__ = 'Shuvro'

Loan_Outstanding_Code = '001001004'
Service_Charges_Code = '001002001'
Admission_Fees_Code = '001002002'
Bank_Interest_Collection_Code = '001002003'
Bank_Balance_Code = '001003001'
Cash_In_Hand_Code = '001003002'
Actual_Value_Withdrawn_Code = '001005004'

Actual_Value_Total_Savings_CDC_Code = '001005002'
Value_Of_Bank_Charge_Code = '001002004'
Value_Of_Expenditure_Code = '001002005'
Interest_Expense_Member_Savings_Code = '001002006'
Interest_Payable_Member_Saving_Balance_Code = '001002007'

Income_Amount_Field_Codes = [Loan_Outstanding_Code, Service_Charges_Code, Admission_Fees_Code,
                             Bank_Interest_Collection_Code,
                             Bank_Balance_Code, Cash_In_Hand_Code, Actual_Value_Withdrawn_Code]

Expenditure_Amount_Field_Codes = [Actual_Value_Total_Savings_CDC_Code, Value_Of_Bank_Charge_Code,
                                  Value_Of_Expenditure_Code, Interest_Expense_Member_Savings_Code,
                                  Interest_Payable_Member_Saving_Balance_Code]


def get_scg_member_fund_value_flat_data(wards=list(), from_time=None, to_time=None):
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

    scg_income_queryset = CustomFieldValue.objects.filter(
        field__assigned_code__in=Income_Amount_Field_Codes, cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    scg_expenditure_queryset = CustomFieldValue.objects.filter(
        field__assigned_code__in=Expenditure_Amount_Field_Codes,
        cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    scg_income_values = scg_income_queryset.annotate(total=Cast('value', FloatField())).aggregate(
        Sum('total'))

    scg_expenditure_values = scg_expenditure_queryset.annotate(total=Cast('value', FloatField())).aggregate(
        Sum('total'))

    scg_income_amount = scg_income_values['total__sum'] if scg_income_values['total__sum'] else 0
    scg_expenditure_amount = scg_expenditure_values['total__sum'] if scg_expenditure_values['total__sum'] else 0

    scg_fund_amount = scg_income_amount - scg_expenditure_amount

    return '<h1 style="font-weight:bold">Value of S&C fund (all cities)</h1><div>' \
           '<span style="font-size: 36px;">' + str(thousand_separator(round(scg_fund_amount))) + ' (BDT)</span></div>'


def get_scg_member_fund_value_column_chart_data(wards=list(), from_time=None, to_time=None):
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

    scg_income_queryset = CustomFieldValue.objects.filter(
        field__assigned_code__in=Income_Amount_Field_Codes, cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    scg_expenditure_queryset = CustomFieldValue.objects.filter(
        field__assigned_code__in=Expenditure_Amount_Field_Codes,
        cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    scg_income_values = scg_income_queryset.values('cdcmonthlyreport__cdc__address__geography__parent__name').annotate(
        total=Sum(Cast('value', FloatField())))

    scg_expenditure_values = scg_expenditure_queryset.values(
        'cdcmonthlyreport__cdc__address__geography__parent__name').annotate(
        total=Sum(Cast('value', FloatField())))

    scg_fund_amount_dict = OrderedDict()

    for scg_income_value in scg_income_values:
        city_name = scg_income_value.get('cdcmonthlyreport__cdc__address__geography__parent__name')
        amount = scg_income_value.get('total')
        scg_fund_amount_dict[city_name] = amount

    for scg_expenditure_value in scg_expenditure_values:
        city_name = scg_expenditure_value.get('cdcmonthlyreport__cdc__address__geography__parent__name')
        amount = scg_expenditure_value.get('total')
        if city_name in scg_fund_amount_dict:
            scg_fund_amount_dict[city_name] -= amount

    data = [
        {
            'name': 'S&C fund value',
            'data': list(scg_fund_amount_dict.values())
        }
    ]

    return data, list(scg_fund_amount_dict.keys())




def get_scg_member_fund_value_table_data(wards=list(), from_time=None, to_time=None):
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

    scg_income_queryset = CustomFieldValue.objects.filter(
        field__assigned_code__in=Income_Amount_Field_Codes, cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    scg_expenditure_queryset = CustomFieldValue.objects.filter(
        field__assigned_code__in=Expenditure_Amount_Field_Codes,
        cdcmonthlyreport__pk__in=approved_cdc_monthly_report_ids
    )

    scg_income_values = scg_income_queryset.values('cdcmonthlyreport__cdc__address__geography__parent__name').annotate(
        total=Sum(Cast('value', FloatField())))

    scg_expenditure_values = scg_expenditure_queryset.values(
        'cdcmonthlyreport__cdc__address__geography__parent__name').annotate(
        total=Sum(Cast('value', FloatField())))

    scg_fund_amount_dict = OrderedDict()

    for scg_income_value in scg_income_values:
        city_name = scg_income_value.get('cdcmonthlyreport__cdc__address__geography__parent__name')
        amount = scg_income_value.get('total')
        scg_fund_amount_dict[city_name] = amount

    for scg_expenditure_value in scg_expenditure_values:
        city_name = scg_expenditure_value.get('cdcmonthlyreport__cdc__address__geography__parent__name')
        amount = scg_expenditure_value.get('total')
        if city_name in scg_fund_amount_dict:
            scg_fund_amount_dict[city_name] -= amount


    response_data = list()
    response_data.append(['City/Town', 'Value of S&C fund'])

    total = 0

    for k, v in scg_fund_amount_dict.items():
        response_data.append([k, thousand_separator(round(v))])
        total += v

    response_data.append(['Total (all cities)', thousand_separator(round(total))])

    return response_data