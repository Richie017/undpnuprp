from collections import OrderedDict

from django.db.models import Sum

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.models.cache.pg_member_info_cache import PGMemberInfoCache
from undp_nuprp.reports.utils.thousand_separator import thousand_separator


def get_pgnumber_indicator_table_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)
    queryset = question_responses.values(
        'city__name').order_by('city__name').annotate(count=Sum('pg_count'))

    city_dict = OrderedDict()
    total_pg = 0
    for data in queryset:
        city = data.get('city__name')
        count = data.get('count')
        if not city or not count:
            continue
        if city is not None and city not in city_dict.keys():
            city_dict[city] = 0
        if city is not None:
            city_dict[city] += data.get('count')
            total_pg += city_dict[city]

    response_data = list()
    total_row = ['Total (all cities)', str(total_pg)]
    response_data.append(['City/Town', 'Number of PG Members'])
    for city_name, count in city_dict.items():
        response_data.append([city_name, thousand_separator(count)])
    response_data.append(total_row)
    return response_data


def get_pgnumber_indicator_pie_chart_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)
    queryset = question_responses.values(
        'city__name').order_by('city__name').annotate(count=Sum('pg_count'))

    report_data = list()
    for answer in queryset:
        city = answer['city__name']

        if not city:
            continue

        report_data.append({
            'name': city,
            'y': answer['count']
        })
    report = {
        'name': 'Count',
        'data': report_data
    }
    return [report]


def get_pgnumber_indicator_flat_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)

    queryset = question_responses.filter(city__name__isnull=False).aggregate(pg_count=Sum('pg_count'))

    total_pg = queryset['pg_count']
    if total_pg is None:
        total_pg = 0
    return '<h1 style="font-weight:bold">Number of PG members (all cities)</h1><div><span style="font-size: 36px;">' \
           + str(thousand_separator(total_pg)) + '</span></div>'
