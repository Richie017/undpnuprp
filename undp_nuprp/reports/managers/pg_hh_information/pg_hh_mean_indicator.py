from collections import OrderedDict

from django.db.models.aggregates import Sum

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.models.cache.pg_member_info_cache import PGMemberInfoCache
from undp_nuprp.reports.utils.thousand_separator import thousand_separator


def get_mean_pghh_size_table_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)
    queryset = question_responses.values(
        'city__name'
    ).order_by(
        'city__name'
    ).annotate(
        total_members=Sum('household_member_count'),
        count=Sum('pg_count')
    )

    city_wise_hh_size_dict = OrderedDict()
    total_member = 0
    total_hh = 0
    for m in queryset:
        _city = m['city__name']
        if _city not in city_wise_hh_size_dict.keys():
            city_wise_hh_size_dict[_city] = {
                'total_members': 0, 'count': 0
            }
        city_wise_hh_size_dict[_city]['count'] += m['count']
        total_hh += m['count']
        total_member += m['total_members']
        city_wise_hh_size_dict[_city]['total_members'] += m['total_members']

    if total_hh:
        total_mean_hh = '%.2f' % (total_member / total_hh)
    else:
        total_mean_hh = 'N/A'
    response_data = list()
    response_data.append((['City Corporation', 'Total Members', 'Total HH', 'Mean HH Size']))
    total_row = ['Total', total_member, total_hh, total_mean_hh]
    for key, value in city_wise_hh_size_dict.items():
        li = list()
        li.append(str(key))
        li.append(thousand_separator(int(value['total_members'])))
        li.append(thousand_separator(int(value['count'])))
        if value['count']:
            li.append('%.2f' % (value['total_members'] / value['count']))
        else:
            li.append('N/A')
        response_data.append(li)
    response_data.append(total_row)
    return response_data


def get_mean_pghh_size_flat_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)
    queryset = question_responses.annotate(
        total_members=Sum('household_member_count'),
        count=Sum('pg_count')
    ).values('total_members', 'count')
    pg_members = sum([m['total_members'] for m in queryset])
    no_of_household = sum([m['count'] for m in queryset])
    mean_size = (pg_members / no_of_household) if no_of_household else 0
    if mean_size:
        mean_size = '%.2f' % mean_size
    else:
        mean_size = 'N/A'

    return '<h1 style="font-weight:bold">Mean HH size, all cities</h1><div><span style="font-size: 36px;">' \
           + thousand_separator(mean_size) + '</span></div>'
