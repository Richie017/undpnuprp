"""
    Created by tareq on 3/13/17
"""
from collections import OrderedDict

from django.db.models.aggregates import Sum

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.models.base.cache.question_response_cache import QuestionResponseCache

__author__ = 'Tareq'


def get_dependent_members_indicator_column_chart_data(wards=list(), from_time=None, to_time=None):
    members_dict = {
        '2.4': 'Children (less than 5 years)',
        '2.5': 'Adolescent girls',
        '2.6': 'Disabled'
    }
    role_wise_queryset = QuestionResponseCache.get_role_based_queryset(
        queryset=QuestionResponseCache.objects.filter()
    ).using(BWDatabaseRouter.get_read_database_name())

    question_responses = role_wise_queryset.filter(
        ref_time__gte=from_time,
        ref_time__lte=to_time,
        question_code__in=list(members_dict.keys()))
    if wards:
        question_responses = question_responses.filter(
            ward_id__in=wards)
    queryset = question_responses.values(
        'question_code', 'answer_text',
        'city_name').order_by(
        'city_name', 'answer_text').annotate(
        count=Sum('survey_count')
    )

    city_names = list()
    dependent_dict = dict()
    for answer in queryset:
        city_name = answer[
            'city_name']
        dependent_type = members_dict[answer['question_code']]
        count = answer['count']
        if dependent_type not in dependent_dict:
            dependent_dict[dependent_type] = {
                'name': dependent_type,
                'data': OrderedDict()
            }
        if city_name not in dependent_dict[dependent_type]['data'].keys():
            dependent_dict[dependent_type]['data'][city_name] = {
                'yes': 0, 'no': 0
            }
        _data = dependent_dict[dependent_type]['data'][city_name]

        if answer['answer_text'].lower() == 'yes':
            _data['yes'] += count
        else:
            _data['no'] += count
        if city_name not in city_names:
            city_names.append(city_name)

    series = list()
    for key, value in dependent_dict.items():
        name = value['name']
        data = list()
        for city in city_names:
            if city in value['data'].keys():
                data.append(
                    value['data'][city]['yes'] * 100.0 / (value['data'][city]['yes'] + value['data'][city]['no'])
                )
            else:
                data.append(0)
        series.append({
            'name': name,
            'data': data
        })

    return series, city_names
