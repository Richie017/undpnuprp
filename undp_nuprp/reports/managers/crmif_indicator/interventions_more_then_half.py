from collections import OrderedDict

from django.db.models import Sum, Value, Count
from django.db.models.functions import Coalesce

from undp_nuprp.approvals.config.constants.sif_constants import INTERVENTION_CATEGORIES
from undp_nuprp.approvals.models import CRMIF


def get_interventions_completed_more_than_half(wards=list, from_time=None, to_time=None):
    intervention_types = INTERVENTION_CATEGORIES

    crmif_queryset = CRMIF.objects.all()
    if wards:
        crmif_queryset = crmif_queryset.filter(assigned_cdc__address__geography__id__in=wards)

    city_dict = {}
    head = ['City/Town']
    table_data = []
    city_count = {}
    total = 0
    for key in intervention_types:
        type_ = intervention_types[key]
        city_count[key] = 0
        head.append(key)
        head.append(key + ' (Avg %)')
        crmifs = crmif_queryset.filter(interventions__type_of_intervention__in=type_,
                                   ).values('assigned_city').annotate(
            total_percentage=Coalesce(Sum('interventions__progress_of_intervention_in_percentage'), Value(0)),
            total_interventions=Count(1)
        )
        for crmif in crmifs:
            total_percentage = crmif['total_percentage']
            total_interventions = crmif['total_interventions']
            city = crmif['assigned_city'] or 'Unassigned'
            percentage = round(total_percentage / total_interventions) if total_interventions else 0
            if city not in city_dict:
                city_dict[city] = OrderedDict()
                for key_ in intervention_types:
                    city_dict[city][key_] = (0, 0)
            if percentage > 50:
                city_dict[city][key] = (percentage, total_interventions)
                city_count[key] += total_interventions
                total += total_interventions

    table_data.append(head)
    cities = sorted(city_dict.keys())

    for city in cities:
        table_row = [city]
        for type_ in city_dict[city]:
            pair = city_dict[city][type_]
            perc = str(round(pair[1] / city_count[type_] * 100)) + '%' if city_count[type_] else '-'
            table_row.append(perc + ' (' + str(pair[1]) + ')')
            table_row.append(str(pair[0]) + '%')

        table_data.append(table_row)

    footer = ['Total']

    for key in intervention_types:
        avg = round(city_count[key] / total * 100) if total else '-'
        footer.append(str(avg) + '% (' + str(city_count[key]) + ')')
        footer.append('-')

    table_data.append(footer)

    return table_data
