from django.db.models.aggregates import Sum

from undp_nuprp.approvals.config.constants.sif_constants import INTERVENTION_CATEGORIES
from undp_nuprp.approvals.models.infrastructures.sif.sif import SIF


def get_beneficiary_by_intervention_column_chart(wards=list(), from_time=None, to_time=None):
    intervention_types = INTERVENTION_CATEGORIES
    beneficiary_male_percent_list = []
    beneficiary_female_percent_list = []
    sif_queryset = SIF.objects

    if wards:
        sif_queryset = sif_queryset.filter(assigned_cdc__address__geography__id__in=wards)

    for key in intervention_types:
        intervention_type = intervention_types[key]
        beneficiary_dict = sif_queryset.filter(interventions__type_of_intervention__in=intervention_type).aggregate(
            total_pg_beneficiary=Sum('interventions__number_of_total_pg_member_beneficiary'),
            total_non_pg_beneficiary=Sum('interventions__number_of_total_non_pg_member_beneficiary'))
        total_pg_beneficiary = beneficiary_dict['total_pg_beneficiary'] \
            if beneficiary_dict['total_pg_beneficiary'] is not None else 0
        total_non_pg_beneficiary = beneficiary_dict['total_non_pg_beneficiary'] \
            if beneficiary_dict['total_non_pg_beneficiary'] is not None else 0
        total_beneficiary = total_pg_beneficiary + total_non_pg_beneficiary

        pg_beneficiary_percent = total_pg_beneficiary / total_beneficiary * 100 if total_beneficiary > 0 else 0
        non_pg_beneficiary_percent = total_non_pg_beneficiary / total_beneficiary * 100 if total_beneficiary > 0 else 0
        beneficiary_male_percent_list.append(pg_beneficiary_percent)
        beneficiary_female_percent_list.append(non_pg_beneficiary_percent)

    report_data = (
        {
            'name': 'Number of PG member',
            'data': beneficiary_male_percent_list
        },
        {
            'name': 'Number of Non-PG member',
            'data': beneficiary_female_percent_list
        }
    )

    return report_data, list(intervention_types.keys())


def get_beneficiary_by_intervention_table_data(wards=list(), from_time=None, to_time=None):
    intervention_types = INTERVENTION_CATEGORIES
    table_data = list()
    grand_total_beneficiary = grand_total_pg_beneficiary = grand_total_non_pg_beneficiary = 0
    sif_queryset = SIF.objects

    if wards:
        sif_queryset = sif_queryset.filter(assigned_cdc__address__geography__id__in=wards)

    head = ['Type of Intervention']
    head += [
        {
            'column_name': 'Number of PG member',
            'extra_column_name': 'Number of PG member(%)',
            'split': 'true'
        }
    ]
    head += [
        {
            'column_name': 'Number of Non-PG member',
            'extra_column_name': 'Number of Non-PG member(%)',
            'split': 'true'
        }
    ]
    table_data.append(head)

    for key in intervention_types:
        intervention_type = intervention_types[key]
        beneficiary_dict = sif_queryset.filter(interventions__type_of_intervention__in=intervention_type).aggregate(
            total_pg_beneficiary=Sum('interventions__number_of_total_pg_member_beneficiary'),
            total_non_pg_beneficiary=Sum('interventions__number_of_total_non_pg_member_beneficiary'))
        total_pg_beneficiary = beneficiary_dict['total_pg_beneficiary'] \
            if beneficiary_dict['total_pg_beneficiary'] is not None else 0
        total_non_pg_beneficiary = beneficiary_dict['total_non_pg_beneficiary'] \
            if beneficiary_dict['total_non_pg_beneficiary'] is not None else 0
        total_beneficiary = total_pg_beneficiary + total_non_pg_beneficiary

        grand_total_pg_beneficiary += total_pg_beneficiary
        grand_total_non_pg_beneficiary += total_non_pg_beneficiary
        grand_total_beneficiary += total_beneficiary

        pg_beneficiary_percent = total_pg_beneficiary / total_beneficiary * 100 if total_beneficiary > 0 else 0
        non_pg_beneficiary_percent = total_non_pg_beneficiary / total_beneficiary * 100 if total_beneficiary > 0 else 0
        table_data.append([key, '{}% ({})'.format(round(pg_beneficiary_percent), total_pg_beneficiary),
                           '{}% ({})'.format(round(non_pg_beneficiary_percent), total_non_pg_beneficiary)])

    grand_total_pg_beneficiary_percent = grand_total_pg_beneficiary / grand_total_beneficiary * 100 \
        if grand_total_beneficiary else 0
    grand_total_non_pg_beneficiary_percent = grand_total_non_pg_beneficiary / grand_total_beneficiary * 100 \
        if grand_total_beneficiary else 0

    table_data.append(
        ['Total', '{}% ({})'.format(round(grand_total_pg_beneficiary_percent), grand_total_pg_beneficiary),
         '{}% ({})'.format(round(grand_total_non_pg_beneficiary_percent), grand_total_non_pg_beneficiary)])

    return table_data
