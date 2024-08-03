from collections import OrderedDict

from undp_nuprp.approvals.config.constants.sif_constants import INTERVENTION_CATEGORIES
from undp_nuprp.approvals.models import CRMIF


def get_intervention_type_pie_chart(wards=list(), from_time=None, to_time=None):
    intervention_types = INTERVENTION_CATEGORIES
    data = list()
    for key in intervention_types:
        intervention_type = intervention_types[key]
        count = CRMIF.objects.filter(interventions__type_of_intervention__in=intervention_type).count()
        data.append({
            'name': key,
            'y': count
        })

    report = [
        {
            'name': 'Number of interventions, by type',
            'data': data
        }
    ]

    return report


def get_intervention_type_table_data(wards=list(), from_time=None, to_time=None):
    crmif_queryset = CRMIF.objects

    if wards:
        crmif_queryset = crmif_queryset.filter(assigned_cdc__address__geography__id__in=wards)

    intervention_types = INTERVENTION_CATEGORIES
    city_data = OrderedDict()
    total_row = []
    head = ['City/Town']
    for key in intervention_types:
        head.append(dict(column_name=key, split='true', extra_column_name=key + "(%)"))
        intervention_type = intervention_types[key]
        crmifs = crmif_queryset.filter(interventions__type_of_intervention__in=intervention_type)
        total_row.append(crmifs.count())
        for crmif in crmifs:
            city = crmif.assigned_city
            city_dict = city_data.get(city, None)
            if city_dict is None:
                city_dict = OrderedDict()
                city_data[city] = city_dict
                for _type in intervention_types:
                    city_data[city][_type] = 0

            city_dict[key] = city_dict[key] + 1

    table_data = list()

    table_data.append(head)

    grand_total_intervention = 0
    footer_row = ['Total (all cities)']

    for city in city_data:
        row = [city]
        total = sum(city_data[city][x] for x in city_data[city])
        for intervention in city_data[city]:
            percentage = city_data[city][intervention] * 100 / total if total else 0
            percentage = round(percentage)
            intervention_stat = "{}% ({})".format(percentage, city_data[city][intervention])
            row.append(intervention_stat)
            grand_total_intervention += city_data[city][intervention]

        table_data.append(row)

    for tr in total_row:
        percentage = tr / grand_total_intervention * 100 if grand_total_intervention > 0 else 0
        footer_row.append('{}% ({})'.format(round(percentage), tr))

    table_data.append(footer_row)

    return table_data
