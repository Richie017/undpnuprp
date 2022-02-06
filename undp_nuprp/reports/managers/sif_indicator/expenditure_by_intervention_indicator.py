from django.db.models.aggregates import Sum

from undp_nuprp.approvals.models.infrastructures.sif.sif import SIF
from undp_nuprp.reports.utils.thousand_separator import thousand_separator


def get_expenditure_by_intervention_flat_data(wards=list(), from_time=None, to_time=None):
    total_number_of_contract = SIF.objects.aggregate(total=Sum('installments__installment_value'))['total']
    total_number_of_contract = total_number_of_contract if total_number_of_contract else 0

    return '<h1 style="font-weight:bold">Expenditure to date (all cities)</h1>' \
           '<div><span style="font-size: 36px;">' + \
           "{0} (BDT)".format(thousand_separator(total_number_of_contract)) + '</span></div>'


def get_expenditure_by_intervention_table_data(wards=list(), from_time=None, to_time=None):
    sif_queryset = SIF.objects
    head = ['City/Town']
    head += [{
        'column_name': 'Expenditure (BDT)',
        'extra_column_name': 'Expenditure (BDT)' + "(%)",
        'split': 'true'
    }]

    if wards:
        sif_queryset = sif_queryset.filter(assigned_cdc__address__geography__id__in=wards)

    sifs = sif_queryset.values('assigned_city').annotate(total=Sum('installments__installment_value'))

    table_data = list()
    table_data.append(head)
    grand_total_expenditure = sif_queryset.aggregate(total=Sum('installments__installment_value'))
    grand_total_expenditure = grand_total_expenditure['total'] if grand_total_expenditure['total'] is not None else 0

    for sif in sifs:
        city = sif['assigned_city']
        total_expenditure = sif['total'] if sif['total'] is not None else 0
        percentage = total_expenditure / grand_total_expenditure * 100 if grand_total_expenditure > 0 else 0
        table_data.append([city, '{}% ({})'.format(round(percentage), total_expenditure)])

    table_data.append(
        ['Total (all cities)', '{}% ({})'.format(100 if grand_total_expenditure > 0 else 0, grand_total_expenditure)])
    return table_data
