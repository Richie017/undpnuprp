import time
from collections import OrderedDict

from django.db.models import Sum

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.config.constants.pg_survey_constants import *
from undp_nuprp.reports.models.cache.pg_member_info_cache import PGMemberInfoCache
from undp_nuprp.reports.utils.thousand_separator import thousand_separator

__author__ = "Shama"


def get_pgage_indicator_pie_chart_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)

    queryset = question_responses.values('age_group_counts__label').order_by(
        'age_group_counts__label').annotate(count=Sum('age_group_counts__count'))

    report_data = list()
    report_dict = OrderedDict()
    age_range_list = PG_MEMBER_AGE_RANGE_LIST
    for _age_range in age_range_list:
        report_dict[_age_range] = {
            'name': _age_range,
            'y': 0
        }

    for answer in queryset:
        try:
            age_range = ''
            if int(answer['age_group_counts__label']) < 0:
                age_range = 'Below 20'
            elif int(answer['age_group_counts__label']) > 100:
                age_range = 'Above 60 and above'
            else:
                pg_age = (int(answer['age_group_counts__label']) * PG_MEMBER_AGE_GROUP_STEP + PG_MEMBER_AGE_LOWER_LIMIT)
                if pg_age:
                    age_range = '%d-%d' % (pg_age, (pg_age + PG_MEMBER_AGE_GROUP_STEP - 1))
            if not age_range:
                continue
            report_dict[age_range]['y'] = answer['count']
        except:
            pass

    for data in report_dict.values():
        report_data.append(data)

    report = {
        'name': 'Count',
        'data': report_data
    }
    return [report]


def get_pgage_indicator_table_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)

    queryset = question_responses.values('city__name', 'age_group_counts__label').order_by(
        'city__name', 'age_group_counts__label').annotate(count=Sum('age_group_counts__count'))

    age_range_list = PG_MEMBER_AGE_RANGE_LIST
    age_range_dict = OrderedDict()

    for _age_range in age_range_list:
        age_range_dict[_age_range] = 0

    for data in queryset:
        try:
            age_range = ''
            if int(data.get('age_group_counts__label')) < 0:
                age_range = 'Below 20'
            elif int(data.get('age_group_counts__label')) > 100:
                age_range = '60 and above'
            else:
                pg_age = (int(data.get('age_group_counts__label'))
                          * PG_MEMBER_AGE_GROUP_STEP + PG_MEMBER_AGE_LOWER_LIMIT)
                if pg_age:
                    age_range = '%d-%d' % (pg_age, (pg_age + PG_MEMBER_AGE_GROUP_STEP - 1))
        except:
            continue
        if not age_range:
            continue
        if age_range:
            age_range_dict[age_range] += data.get('count')

    table_data = OrderedDict()
    for data in queryset:
        city = data.get('city__name')
        count = data.get('count')
        if not city or not count:
            continue
        try:
            age_range = ''
            if int(data.get('age_group_counts__label')) < 0:
                age_range = 'Below 20'
            elif int(data.get('age_group_counts__label')) > 100:
                age_range = '60 and above'
            else:
                pg_age = (int(data.get('age_group_counts__label'))
                          * PG_MEMBER_AGE_GROUP_STEP + PG_MEMBER_AGE_LOWER_LIMIT)
                if pg_age:
                    age_range = '%d-%d' % (pg_age, (pg_age + PG_MEMBER_AGE_GROUP_STEP - 1))
        except:
            continue
        if city not in table_data.keys():
            table_data[city] = OrderedDict()
            for c in age_range_dict.keys():
                table_data[city][c] = 0
        if age_range:
            table_data[city][age_range] = "{0}".format(count)

    table_data['Total'] = OrderedDict()
    for c in age_range_dict.keys():
        table_data['Total'][c] = age_range_dict[c]

    city_pg_dict = dict()
    all_cities_pgm = 0
    for data in queryset:
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
    for _item in age_range_dict.keys():
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


def print_current_time(msg=None, previous_time=time.time()):
    t = time.time()
    print("{}: {}, time taken: {} s".format(t, msg, (t - previous_time)))
    return t
