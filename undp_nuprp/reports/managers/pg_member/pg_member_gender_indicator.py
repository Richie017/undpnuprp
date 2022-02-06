"""
Created by tareq on 2/13/18
"""

from collections import OrderedDict

from django.db.models import Sum

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.config.constants.pg_survey_constants import PG_MEMBER_GENDER_LIST
from undp_nuprp.reports.models.cache.pg_member_info_cache import PGMemberInfoCache
from undp_nuprp.reports.utils.thousand_separator import thousand_separator

__author__ = 'Tareq'


def get_pggender_indicator_table_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)
    queryset = question_responses.values('city__name', 'gender_counts__label').order_by(
        'city__name', 'gender_counts__label').annotate(count=Sum('gender_counts__count'))

    gender_dict = OrderedDict()
    gender_list = PG_MEMBER_GENDER_LIST
    for _gender in gender_list:
        gender_dict[_gender] = 0

    for data in queryset:
        answer = data.get('gender_counts__label')
        if not answer:
            continue
        if answer not in gender_dict.keys():
            gender_dict[answer] = 0
        gender_dict[answer] += data.get('count')

    table_data = OrderedDict()
    for data in queryset:
        city = data.get('city__name')
        answer = data.get('gender_counts__label')
        count = data.get('count')
        if city is None or answer is None or count is None:
            continue
        if city not in table_data.keys():
            table_data[city] = OrderedDict()
            for c in gender_dict.keys():
                table_data[city][c] = 0

        table_data[city][answer] = "{0}".format(count)

    table_data['Total'] = OrderedDict()
    for c in gender_dict.keys():
        table_data['Total'][c] = gender_dict[c]

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
    for _item in gender_dict.keys():
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


def get_pg_gender_indicator_pie_chart_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(
            ward_id__in=wards)
    queryset = question_responses.values('gender_counts__label').annotate(
        count=Sum('gender_counts__count')).order_by('gender_counts__label')

    report_data = list()
    report_dict = OrderedDict()
    gender_list = PG_MEMBER_GENDER_LIST
    for _gender in gender_list:
        report_dict[_gender] = {
            'name': _gender,
            'y': 0
        }

    for answer in queryset:
        gender = answer['gender_counts__label']
        if not gender:
            continue
        report_dict[gender]['y'] = answer['count']

    for data in report_dict.values():
        report_data.append(data)

    report = {
        'name': 'Count',
        'data': report_data
    }
    return [report]
