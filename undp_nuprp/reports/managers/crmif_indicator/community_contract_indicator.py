from django.db.models.aggregates import Count

from undp_nuprp.approvals.models import CRMIF
from undp_nuprp.reports.utils.thousand_separator import thousand_separator


def get_community_contract_flat_data(wards=list(), from_time=None, to_time=None):
    total_number_of_contract = CRMIF.objects.count()

    return '<h1 style="font-weight:bold">Number of contracts (all cities)</h1>' \
           '<div><span style="font-size: 36px;">' + \
           "{0}".format(thousand_separator(total_number_of_contract)) + '</span></div>'


def get_community_contract_table_data(wards=list(), from_time=None, to_time=None):
    crmif_queryset = CRMIF.objects

    if wards:
        crmif_queryset = crmif_queryset.filter(assigned_cdc__address__geography__id__in=wards)

    city_wise_community_numbers = crmif_queryset.values('assigned_city').annotate(total=Count('id')).order_by(
        'assigned_city')

    total_community_number = crmif_queryset.count()

    table_data = list()

    table_data.append(['City/Town', ] + [{
        'column_name': 'Number of Contracts',
        'extra_column_name': 'Number of Contracts(%)',
        'split': 'true'
    }])

    for city_wise_community_number in city_wise_community_numbers:
        percentage = city_wise_community_number['total'] / total_community_number * 100 if total_community_number else 0
        table_data.append(
            [city_wise_community_number['assigned_city'],
             '{0}% ({1})'.format(round(percentage), city_wise_community_number['total'])])

    table_data.append(['Total (all cities)',
                       '{0}% ({1})'.format('100' if total_community_number > 0 else '0', total_community_number)])

    return table_data
