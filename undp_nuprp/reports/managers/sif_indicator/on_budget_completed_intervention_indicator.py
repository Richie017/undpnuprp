from collections import OrderedDict

from django.db.models.aggregates import Count
from django.db.models.expressions import Case, When

from undp_nuprp.approvals.config.constants.sif_constants import INTERVENTION_CATEGORIES
from undp_nuprp.approvals.models.infrastructures.sif.sif import SIF


def get_on_budget_completed_intervention_column_chart(wards=list(), from_time=None, to_time=None):
    intervention_types = INTERVENTION_CATEGORIES
    data = OrderedDict()
    for key in intervention_types:
        intervention_type = intervention_types[key]
        completed_intervention_info = SIF.objects.filter(
            interventions__type_of_intervention__in=intervention_type).aggregate(
            within_budget=Count(
                Case(When(interventions__completed_contract__within_budget__iexact='yes', then=1))),
            total_sif=Count(1))

        total_within_budget = completed_intervention_info['within_budget'] if completed_intervention_info[
            'within_budget'] else 0
        total_sif = completed_intervention_info['total_sif'] if completed_intervention_info['total_sif'] else 0

        percentage = total_within_budget / total_sif * 100 if total_sif else 0

        data[key] = round(percentage)

    _data = [
        {
            'name': 'Within budget',
            'data': list(data.values())
        }
    ]

    return _data, list(data.keys())


def get_on_budget_completed_intervention_table_data(wards=list(), from_time=None, to_time=None):
    intervention_types = INTERVENTION_CATEGORIES
    table_data = list()
    city_data = OrderedDict()
    intervention_wise_data = dict()
    grand_total_sif = 0
    completed_on_budget_intervention_info = dict()

    sif_queryset = SIF.objects

    if wards:
        sif_queryset = sif_queryset.filter(assigned_cdc__address__geography__id__in=wards)

    head = ['City/Town']
    for key in intervention_types:
        head.append(key + '(%)')
        intervention_type = intervention_types[key]
        completed_on_budget_intervention_info[key] = 0
        completed_intervention_queryset = sif_queryset.filter(
            interventions__type_of_intervention__in=intervention_type).values('assigned_city').annotate(
            within_budget=Count(Case(When(interventions__completed_contract__within_budget__iexact='yes', then=1))),
            total_sif=Count(1))

        for completed_intervention_info in completed_intervention_queryset:
            _city = completed_intervention_info['assigned_city']
            _total_sif = completed_intervention_info['total_sif'] if completed_intervention_info['total_sif'] else 0
            grand_total_sif += _total_sif

            _total_within_budget = completed_intervention_info['within_budget'] if completed_intervention_info[
                'within_budget'] else 0
            completed_on_budget_intervention_info[key] += _total_within_budget

            if _city not in city_data:
                city_data[_city] = OrderedDict()

            if key not in city_data[_city]:
                city_data[_city][key] = (0, 0)

            if key not in intervention_wise_data:
                intervention_wise_data[key] = (0, 0)

            _int_within_bud, _int_tot_sif = intervention_wise_data[key]
            _int_within_bud += _total_within_budget
            _int_tot_sif += _total_sif
            intervention_wise_data[key] = (_int_within_bud, _int_tot_sif)

            _tot_within_bud, _tot_sif = city_data[_city][key]
            _tot_within_bud += _total_within_budget
            _tot_sif += _total_sif
            city_data[_city][key] = (_tot_within_bud, _tot_sif)

    table_data.append(head)

    cities = sorted(city_data.keys())

    for city in cities:
        row_data = [city]
        for intervention_type in intervention_types:
            _total_within_budget, _total_sif = city_data[city][
                intervention_type] if city in city_data and intervention_type in city_data[city] else (0, 0)
            percent = _total_within_budget / _total_sif * 100 if _total_sif else 0
            row_data.append(round(percent))

        table_data.append(row_data)

    row_data = ['Total']
    for intervention_type in intervention_types:
        _total_within_budget, _total_sif = intervention_wise_data[
            intervention_type] if intervention_type in intervention_wise_data else (0, 0)
        percent = _total_within_budget / _total_sif * 100 if _total_sif else 0
        row_data.append(round(percent))

    table_data.append(row_data)

    return table_data
