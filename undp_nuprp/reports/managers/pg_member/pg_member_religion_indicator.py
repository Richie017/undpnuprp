from collections import OrderedDict

from django.db.models import Sum

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.config.constants.pg_survey_constants import *
from undp_nuprp.reports.models.cache.pg_member_info_cache import PGMemberInfoCache
from undp_nuprp.reports.utils.thousand_separator import thousand_separator


def get_pgreligion_indicator_pie_chart_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)

    queryset = question_responses.values('religion_counts__label').annotate(
        count=Sum('religion_counts__count')).order_by('-count', 'religion_counts__label')

    report_data = list()
    report_dict = OrderedDict()
    religion_list = PG_MEMBER_RELIGION_LIST
    for _religion in religion_list:
        report_dict[_religion] = {
            'name': _religion,
            'y': 0
        }

    for answer in queryset:
        religion = answer['religion_counts__label']
        if not religion:
            continue

        if religion in report_dict.keys():
            report_dict[religion]['y'] = answer['count']
        else:
            report_dict['Other']['y'] += answer['count']

    for data in report_dict.values():
        report_data.append(data)

    report = {
        'name': 'Count',
        'data': report_data
    }
    return [report]


def get_pgreligion_indicator_table_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)

    religion_list = PG_MEMBER_RELIGION_LIST

    queryset = question_responses.values('religion_counts__label', 'city__name').annotate(
        count=Sum('religion_counts__count')
    ).order_by('-count', 'city__name', 'religion_counts__label')

    all_queryset = question_responses.values('city__name', 'religion_counts__label').order_by(
        'city__name', 'religion_counts__label').annotate(count=Sum('religion_counts__count'))

    religion_dict = OrderedDict()
    for _religion in religion_list:
        religion_dict[_religion] = 0

    for data in queryset:
        religion_name = data.get('religion_counts__label')
        count = data.get('count')
        if not religion_name or not count:
            continue

        if religion_name in religion_dict.keys():
            religion_dict[religion_name] += count
        else:
            religion_dict['Other'] += count

    table_data = OrderedDict()
    for data in queryset:
        city = data.get('city__name')
        religion_name = data.get('religion_counts__label')
        count = data.get('count')
        if city is None or religion_name is None or count is None:
            continue
        if city not in table_data.keys():
            table_data[city] = OrderedDict()
            for c in religion_dict.keys():
                table_data[city][c] = 0

        if religion_name in table_data[city].keys():
            table_data[city][religion_name] = count
        else:
            table_data[city]['Other'] += count

    table_data['Total'] = OrderedDict()
    for c in religion_dict.keys():
        table_data['Total'][c] = religion_dict[c]

    city_pg_dict = dict()
    all_cities_pgm = 0
    for data in all_queryset:
        city = data.get('city__name')
        count = data.get('count')
        if not city or not count:
            continue
        if city is not None and city not in city_pg_dict.keys():
            city_pg_dict[city] = 0
        city_pg_dict[city] += count
        all_cities_pgm += count

    response_data = list()
    table_headings = list()
    for _item in religion_dict.keys():
        table_headings.append({
            'column_name': str(_item),
            'extra_column_name': str(_item) + "(%)",
            'split': 'true'
        })
    response_data.append((['City/Town', ] + table_headings))
    for key, value in table_data.items():
        li = [str(key)]
        for k, v in value.items():
            if key in city_pg_dict.keys():
                if city_pg_dict[key] > 0:
                    li.append("{0:.0f}%".format(float(v) / city_pg_dict[key] * 100) + ' (' + thousand_separator(int(v)) + ')')
            else:
                if all_cities_pgm > 0:
                    li.append("{0:.0f}%".format(float(v) / all_cities_pgm * 100) + ' (' + thousand_separator(int(v)) + ')')
        response_data.append(li)
    return response_data
