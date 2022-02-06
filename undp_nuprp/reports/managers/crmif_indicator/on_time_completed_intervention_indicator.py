from collections import OrderedDict

from django.db.models.aggregates import Count
from django.db.models.expressions import Case, When

from undp_nuprp.approvals.config.constants.sif_constants import INTERVENTION_CATEGORIES
from undp_nuprp.approvals.models import CRMIF


def get_on_time_completed_intervention_column_chart(wards=list(), from_time=None, to_time=None):
    intervention_types = INTERVENTION_CATEGORIES
    data = OrderedDict()
    for key in intervention_types:
        intervention_type = intervention_types[key]
        completed_intervention_info = CRMIF.objects.filter(
            interventions__type_of_intervention__in=intervention_type).aggregate(
            total_on_time=Count(
                Case(When(interventions__completed_contract__completed_as_expected_date__iexact='yes', then=1))),
            total_crmif=Count(1))

        total_on_time = completed_intervention_info['total_on_time'] if completed_intervention_info[
            'total_on_time'] else 0
        total_crmif = completed_intervention_info['total_crmif'] if completed_intervention_info['total_crmif'] else 0

        percentage = total_on_time / total_crmif * 100 if total_crmif else 0

        data[key] = round(percentage)

    _data = [
        {
            'name': 'Completed on time',
            'data': list(data.values())
        }
    ]

    return _data, list(data.keys())


def get_on_time_completed_intervention_table_data(wards=list(), from_time=None, to_time=None):
    intervention_types = INTERVENTION_CATEGORIES
    table_data = list()
    city_data = OrderedDict()
    intervention_wise_data = dict()
    grand_total_crmif = 0
    completed_on_time_intervention_info = dict()

    crmif_queryset = CRMIF.objects

    if wards:
        crmif_queryset = crmif_queryset.filter(assigned_cdc__address__geography__id__in=wards)

    head = ['City/Town']
    for key in intervention_types:
        head.append(key + '(%)')
        intervention_type = intervention_types[key]
        completed_on_time_intervention_info[key] = 0
        completed_intervention_queryset = crmif_queryset.filter(
            interventions__type_of_intervention__in=intervention_type).values(
            'assigned_city').annotate(total_on_time=Count(
            Case(When(interventions__completed_contract__completed_as_expected_date__iexact='yes', then=1))),
            total_crmif=Count(1))

        for completed_intervention_info in completed_intervention_queryset:
            _city = completed_intervention_info['assigned_city']
            _total_crmif = completed_intervention_info['total_crmif'] if completed_intervention_info[
                'total_crmif'] else 0
            grand_total_crmif += _total_crmif

            _total_on_time = completed_intervention_info['total_on_time'] if completed_intervention_info[
                'total_on_time'] else 0
            completed_on_time_intervention_info[key] += _total_on_time

            if _city not in city_data:
                city_data[_city] = OrderedDict()

            if key not in city_data[_city]:
                city_data[_city][key] = (0, 0)

            if key not in intervention_wise_data:
                intervention_wise_data[key] = (0, 0)

            _int_tot_time, _int_tot_crmif = intervention_wise_data[key]
            _int_tot_time += _total_on_time
            _int_tot_crmif += _total_crmif
            intervention_wise_data[key] = (_int_tot_time, _int_tot_crmif)

            _tot_time, _tot_crmif = city_data[_city][key]
            _tot_time += _total_on_time
            _tot_crmif += _total_crmif
            city_data[_city][key] = (_tot_time, _tot_crmif)

    table_data.append(head)

    cities = sorted(city_data.keys())

    for city in cities:
        row_data = [city]
        for intervention_type in intervention_types:
            _total_on_time, _total_crmif = city_data[city][
                intervention_type] if city in city_data and intervention_type in city_data[city] else (0, 0)
            percent = _total_on_time / _total_crmif * 100 if _total_crmif else 0
            row_data.append(round(percent))

        table_data.append(row_data)

    row_data = ['Total']
    for intervention_type in intervention_types:
        _total_on_time, _total_crmif = intervention_wise_data[
            intervention_type] if intervention_type in intervention_wise_data else (0, 0)
        percent = _total_on_time / _total_crmif * 100 if _total_crmif else 0
        row_data.append(round(percent))

    table_data.append(row_data)

    return table_data
