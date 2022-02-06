from collections import OrderedDict

from django.db.models.aggregates import Sum
from django.db.models.expressions import F

from undp_nuprp.approvals.config.constants.sif_constants import INTERVENTION_CATEGORIES
from undp_nuprp.approvals.models.infrastructures.sif.sif import SIF


def get_gender_by_intervention_stacked_column_chart(wards=list(), from_time=None, to_time=None):
    intervention_categories_by_type = INTERVENTION_CATEGORIES
    gender_wise_intervention = OrderedDict([('male', OrderedDict()), ('female', OrderedDict())])
    sif_queryset = SIF.objects

    if wards:
        sif_queryset = sif_queryset.filter(assigned_cdc__address__geography__id__in=wards)

    for intervention_category, intervention_types in intervention_categories_by_type.items():
        total_male = sif_queryset.filter(
            interventions__type_of_intervention__in=intervention_types).aggregate(total=Sum(
            F('interventions__number_of_male_pg_member_beneficiary') +
            F('interventions__number_of_male_non_pg_member_beneficiary')))['total']
        total_female = sif_queryset.filter(
            interventions__type_of_intervention__in=intervention_types).aggregate(total=Sum(
            F('interventions__number_of_female_pg_member_beneficiary') +
            F('interventions__number_of_female_non_pg_member_beneficiary')))['total']

        total_male = total_male if total_male else 0
        total_female = total_female if total_female else 0
        total_male_female = total_male + total_female

        male_percent_this_intervention = total_male / total_male_female * 100 if total_male > 0 else 0
        female_percent_this_intervention = total_female / total_male_female * 100 if total_female > 0 else 0

        gender_wise_intervention['male'][intervention_category] = male_percent_this_intervention
        gender_wise_intervention['female'][intervention_category] = female_percent_this_intervention

    data = [
        {
            'name': 'Male',
            'data': [male_percent for male_percent in gender_wise_intervention['male'].values()]
        },
        {
            'name': 'Female',
            'data': [female_percent for female_percent in gender_wise_intervention['female'].values()]
        }
    ]

    return data, list(intervention_categories_by_type.keys())


def get_gender_by_intervention_table_data(wards=list(), from_time=None, to_time=None):
    intervention_categories_by_type = INTERVENTION_CATEGORIES
    sif_queryset = SIF.objects
    table_data = list()

    if wards:
        sif_queryset = sif_queryset.filter(assigned_cdc__address__geography__id__in=wards)

    head = ['Type of Intervention']
    head += [
        {
            'column_name': 'Male',
            'extra_column_name': "Male(%)",
            'split': 'true'
        }
    ]
    head += [
        {
            'column_name': 'Female',
            'extra_column_name': "Female(%)",
            'split': 'true'
        }
    ]

    table_data.append(head)
    grand_total_male = grand_total_female = 0

    for intervention_category, intervention_types in intervention_categories_by_type.items():
        total_male = sif_queryset.filter(
            interventions__type_of_intervention__in=intervention_types).aggregate(total=Sum(
            F('interventions__number_of_male_pg_member_beneficiary') +
            F('interventions__number_of_male_non_pg_member_beneficiary')))['total']
        total_female = sif_queryset.filter(
            interventions__type_of_intervention__in=intervention_types).aggregate(total=Sum(
            F('interventions__number_of_female_pg_member_beneficiary') +
            F('interventions__number_of_female_non_pg_member_beneficiary')))['total']

        total_male = total_male if total_male else 0
        total_female = total_female if total_female else 0
        total_male_female = total_male + total_female

        grand_total_male += total_male
        grand_total_female += total_female

        male_percent_this_intervention = total_male / total_male_female * 100 if total_male > 0 else 0
        female_percent_this_intervention = total_female / total_male_female * 100 if total_female > 0 else 0

        table_data.append([intervention_category, '{}% ({})'.format(round(male_percent_this_intervention), total_male),
                           '{}% ({})'.format(round(female_percent_this_intervention), total_female)])

    grand_total_male_female = grand_total_male + grand_total_female
    grand_total_male_percent = grand_total_male / grand_total_male_female * 100 if grand_total_male_female > 0 else 0
    grand_total_female_percent = grand_total_female / grand_total_male_female * 100 \
        if grand_total_male_female > 0 else 0

    table_data.append(['Total', '{}% ({})'.format(round(grand_total_male_percent), grand_total_male),
                       '{}% ({})'.format(round(grand_total_female_percent), grand_total_female)])

    return table_data
