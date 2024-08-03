"""
    Created by tareq on 3/13/17
"""
from django.db.models.aggregates import Count, Sum
from collections import OrderedDict

from django.db.models.fields import IntegerField
from django.db.models.functions.base import Cast

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.models.base.cache.question_response_cache import QuestionResponseCache

__author__ = 'Tareq'


def get_mean_household_size_data(wards=list(), from_time=None, to_time=None):
    role_wise_queryset = QuestionResponseCache.get_role_based_queryset(
        queryset=QuestionResponseCache.objects.filter()
    ).using(BWDatabaseRouter.get_read_database_name())
    question_responses = role_wise_queryset.filter(
        ref_time__gte=from_time,
        ref_time__lte=to_time, question_code='2.1')
    if wards:
        question_responses = question_responses.filter(
            ward_id__in=wards)
    members_queryset = question_responses.annotate(members=Cast('answer_text', IntegerField())).values('members', 'survey_count')
    members = [m['members'] * m['survey_count'] for m in members_queryset]
    no_of_household = sum([m['survey_count'] for m in members_queryset])
    mean_size = sum(members) / no_of_household if no_of_household else 0
    if mean_size:
        mean_size = '%.2f' % mean_size
    else:
        mean_size = 'N/A'

    return '<h1>Mean HH size for all Sampled Households, all cities</h1><div><span style="font-size: 36px;">' + mean_size + '</span></div>'


def get_mean_household_size_table_data(wards=list(), from_time=None, to_time=None):
    role_wise_queryset = QuestionResponseCache.get_role_based_queryset(
        queryset=QuestionResponseCache.objects.filter()
    ).using(BWDatabaseRouter.get_read_database_name())
    question_responses = role_wise_queryset.filter(
        ref_time__gte=from_time,
        ref_time__lte=to_time, question_code='2.1')
    if wards:
        question_responses = question_responses.filter(
            ward_id__in=wards)
    members = question_responses.annotate(members=Cast('answer_text', IntegerField())).values('members',
              'survey_count', 'city_name')
    city_wise_hh_size_dict = OrderedDict()
    for m in members:
        if m['city_name'] not in city_wise_hh_size_dict.keys():
            city_wise_hh_size_dict[m['city_name']] = {
                'total_members': 0, 'survey_count': 0
            }
        city_wise_hh_size_dict[m['city_name']]['survey_count'] += m['survey_count']
        city_wise_hh_size_dict[m['city_name']]['total_members'] += m['survey_count']*m['members']


    response_data = list()
    response_data.append((['City Corporation', 'Total Members', 'Total HH', 'Mean HH Size']))
    for key, value in city_wise_hh_size_dict.items():
        li = [str(key)]
        li.append(value['total_members'])
        li.append(value['survey_count'])
        if value['survey_count']:
            li.append('%.2f' % (value['total_members']/value['survey_count']))
        else:
            li.append('N/A')
        response_data.append(li)
    return response_data


