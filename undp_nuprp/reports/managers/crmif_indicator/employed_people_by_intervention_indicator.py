from collections import OrderedDict

from django.db.models.aggregates import Sum

from undp_nuprp.approvals.config.constants.sif_constants import INTERVENTION_CATEGORIES
from undp_nuprp.approvals.models import CRMIF


def get_employed_people_by_intervention_column_chart(wards=list(), from_time=None, to_time=None):
    intervention_types = INTERVENTION_CATEGORIES
    data = OrderedDict()
    for key in intervention_types:
        intervention_type = intervention_types[key]
        total_employed = CRMIF.objects.filter(interventions__type_of_intervention__in=intervention_type).aggregate(
            total=Sum('interventions__completed_contract__number_of_people_employed'))
        data[key] = total_employed['total'] if total_employed['total'] is not None else 0

    _data = [
        {
            'name': 'Total number of people employed',
            'data': list(data.values())
        }
    ]

    return _data, list(data.keys())


def get_employed_people_by_intervention_table_data(wards=list(), from_time=None, to_time=None):
    intervention_types = INTERVENTION_CATEGORIES
    cities = set()
    city_wise_intervention_total = dict()
    city_wise_total_employed = dict()
    intervention_wise_total = dict()

    head = ['City/Town']
    grand_total_person_employed = 0

    for key in intervention_types:
        head += [
            {
                'column_name': key,
                'extra_column_name': key + "(%)",
                'split': 'true'
            }
        ]
        intervention_type = intervention_types[key]
        crmif_queryset = CRMIF.objects.filter(interventions__type_of_intervention__in=intervention_type).annotate(
            total=Sum('interventions__completed_contract__number_of_people_employed')).values('assigned_city', 'total')

        for crmif in crmif_queryset:
            _city = crmif['assigned_city']
            cities.add(_city)
            _total_person_employed = crmif['total'] if crmif['total'] is not None else 0

            if _city not in city_wise_total_employed:
                city_wise_total_employed[_city] = 0

            if _city not in city_wise_intervention_total:
                city_wise_intervention_total[_city] = dict()

            if key not in city_wise_intervention_total[_city]:
                city_wise_intervention_total[_city][key] = 0

            if key not in intervention_wise_total:
                intervention_wise_total[key] = 0

            city_wise_total_employed[_city] += _total_person_employed
            city_wise_intervention_total[_city][key] += _total_person_employed
            intervention_wise_total[key] += _total_person_employed
            grand_total_person_employed += _total_person_employed

    table_data = list()

    table_data.append(head)

    for city in sorted(cities):
        row = [city]
        for intervention_type in intervention_types.keys():
            intervention_total = city_wise_intervention_total[
                city][intervention_type] if city in city_wise_intervention_total and intervention_type in \
                                                                                     city_wise_intervention_total[
                                                                                         city] else 0
            city_total = city_wise_total_employed[city] if city in city_wise_total_employed else 0

            percentage = intervention_total / city_total * 100 if city_total > 0 else 0
            row.append('{0}% ({1})'.format(round(percentage), intervention_total))

        table_data.append(row)

    footer_row = ['Total (all cities)']

    for intervention_type in intervention_types.keys():
        intervention_total = intervention_wise_total[
            intervention_type] if intervention_type in intervention_wise_total else 0
        percentage = intervention_total / grand_total_person_employed * 100 if grand_total_person_employed > 0 else 0
        footer_row.append('{}% ({})'.format(round(percentage), intervention_total))

    table_data.append(footer_row)

    return table_data
