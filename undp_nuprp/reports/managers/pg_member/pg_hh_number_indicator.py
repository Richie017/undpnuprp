from collections import OrderedDict

from django.db.models import Sum

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.models.cache.pg_member_info_cache import PGMemberInfoCache
from undp_nuprp.reports.utils.thousand_separator import thousand_separator


def get_pg_hh_status_indicator_table_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)

    queryset = question_responses.values('city__name').order_by(
        'city__name').annotate(count=Sum('household_head_count'), pg_count=Sum('pg_count'))

    city_dict = OrderedDict()
    city_pg_dict = OrderedDict()
    total_hh_head = 0
    total_pg = 0
    for data in queryset:
        city = data.get('city__name')
        pg_count = data.get('pg_count')
        count = data.get('count')
        if not city or not pg_count or not count:
            continue
        if city is not None and city not in city_dict.keys():
            city_dict[city] = 0
        if city is not None:
            city_dict[city] += count
            total_hh_head += count
            total_pg += pg_count

    for data in queryset:
        city = data.get('city__name')
        pg_count = data.get('pg_count')
        if not city or not pg_count:
            continue
        if city is not None and city not in city_pg_dict.keys():
            city_pg_dict[city] = 0
        if city is not None:
            city_pg_dict[city] += pg_count

    if total_pg > 0:
        hh_percentage = float(total_hh_head) / total_pg * 100
    else:
        hh_percentage = 0
    total_row = ['Total (all cities)', "{0:.0f}%".format(hh_percentage) + ' (' + str(total_hh_head) + ')']

    response_data = list()
    table_headings = list()
    table_headings.append({
        'column_name': 'Number of PG Members(HH Head)',
        'extra_column_name': "Number of PG Members(HH Head)(%)",
        'split': 'true'
    }, )
    response_data.append(['City/Town', ] + table_headings)
    for city, count in city_dict.items():
        response_data.append(
            [city, "{0:.0f}%".format(float(count) / city_pg_dict[city] * 100) + ' (' + thousand_separator(int(count)) + ')'])
    response_data.append(total_row)
    return response_data


def get_pg_hh_status_indicator_pie_chart_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)

    queryset = question_responses.values('city__name').order_by(
        'city__name').annotate(count=Sum('household_head_count'))

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


def get_pg_hh_status_indicator_flat_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)

    queryset = question_responses.filter(city__name__isnull=False).aggregate(
        count=Sum('household_head_count'), pg_count=Sum('pg_count'))

    total_hh = queryset['count']
    total_pg = queryset['pg_count']
    if total_hh is None:
        total_hh = 0
    result = "{0:.0f}%".format(float(total_hh) / total_pg * 100)

    return '<h1 style="font-weight:bold">% of PG members who are HH head (all cities)</h1><div><span style="font-size: 36px;">' + \
           thousand_separator(result) + ' (' + str(thousand_separator(total_hh)) + ')' + '</span></div>'
