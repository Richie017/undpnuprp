"""
    Created by tareq on 3/13/17
"""
from collections import OrderedDict
import time

from django.db.models.aggregates import Count, Sum

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.models.base.cache.question_response_cache import QuestionResponseCache

__author__ = 'Tareq'


def get_gender_indicator_pie_chart_data(wards=list(), from_time=None, to_time=None):
    # role_wise_queryset = QuestionResponseCache.get_role_based_queryset(
    #     queryset=QuestionResponseCache.objects.filter()
    # )

    msg = 'Pi chart'

    pt = print_current_time(msg + '-1')
    question_responses = QuestionResponseCache.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
        ref_time__gte=from_time,
        ref_time__lt=to_time,
        question_code='1.5')
    if wards:
        question_responses = question_responses.filter(
            ward_id__in=wards)
    queryset = question_responses.values('answer_text').annotate(
        count=Sum('survey_count')).order_by('answer_text')

    pt = print_current_time(msg + '-2', pt)
    report_data = list()
    for answer in queryset:
        pt = print_current_time(msg + '-2.5', pt)
        gender = answer['answer_text']
        # Adding hijra definition
        if gender.lower() == 'hijra':
            hijra_define = 'A person whose gender identity is neither male nor female.'
            gender = '<div class="hastip" title="{}">{} Headed Household</div>'.format(hijra_define, gender)
            report_data.append({
                'name': gender,
                'y': answer['count']
            })
            continue

        report_data.append({
            'name': gender + ' Headed Household',
            'y': answer['count']
        })
        pt = print_current_time(msg + '-3', pt)
    report = {
        'name': 'Count',
        'data': report_data
    }
    pt = print_current_time(msg + '-4', pt)
    return [report]


def get_gender_indicator_column_chart_data(wards=list(), from_time=None, to_time=None):
    # role_wise_queryset = QuestionResponseCache.get_role_based_queryset(
    #     queryset=QuestionResponseCache.objects.filter()
    # )
    question_responses = QuestionResponseCache.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
        ref_time__gte=from_time,
        ref_time__lte=to_time,
        question_code='1.5')
    if wards:
        question_responses = question_responses.filter(
            ward_id__in=wards)
    queryset = question_responses.values(
        'answer_text',
        'city_name').order_by(
        'city_name', 'answer_text').annotate(
        count=Sum('survey_count'))

    city_names = list()
    gender_dict = OrderedDict()
    total_dict = OrderedDict()
    for answer in queryset:
        city_name = answer[
            'city_name']
        gender = answer['answer_text']
        if gender.lower() == 'hijra':
            hijra_define = 'A person whose gender identity is neither male nor female.'
            # set holding text for Hijra/Other
            gender = '<div class="hastip" title="{}">{}</div>'.format(hijra_define, gender)
        count = answer['count']
        if gender not in gender_dict:
            gender_dict[gender] = {
                'name': gender,
                'data': OrderedDict()
            }
        gender_dict[gender]['data'][city_name] = count
        if city_name not in city_names:
            city_names.append(city_name)
            total_dict[city_name] = 0
        total_dict[city_name] += count

    series = list()
    for key, value in gender_dict.items():
        name = value['name']
        data = list()
        for city in city_names:
            if city in value['data'].keys():
                data.append(value['data'][city] * 100.0 / total_dict[city])
            else:
                data.append(0)
        series.append({
            'name': name,
            'data': data,
            'useHTML': True
        })

    return series, city_names


def get_gender_indicator_table_data(wards=list(), from_time=None, to_time=None):
    # role_wise_queryset = QuestionResponseCache.get_role_based_queryset(
    #     queryset=QuestionResponseCache.objects.filter()
    # )
    question_responses = QuestionResponseCache.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
        ref_time__gte=from_time,
        ref_time__lte=to_time,
        question_code='1.5')
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)
    queryset = question_responses.values('answer_text', 'city_name').order_by(
        'answer_text', 'city_name'
    ).annotate(count=Sum('survey_count'))

    city_dict = OrderedDict()
    for data in queryset:
        city = data.get('city_name') + '(Total)'
        city_percentage = data.get('city_name') + '(%)'
        if city not in city_dict.keys():
            city_dict[city] = 0
            city_dict[city_percentage] = 0
        city_dict[city] += data.get('count')

    table_data = OrderedDict()
    for data in queryset:
        city = data.get('city_name') + '(Total)'
        city_percentage = data.get('city_name') + '(%)'
        answer = data.get('answer_text')
        count = data.get('count')

        if answer not in table_data.keys():
            table_data[answer] = OrderedDict()
            for c in city_dict.keys():
                table_data[answer][c] = 'N/A'

        table_data[answer][city] = "{0}".format(count)
        table_data[answer][city_percentage] = "{0}".format(float("{0:.2f}".format(((count / city_dict[city]) * 100))))

    response_data = list()
    response_data.append((['Gender', ] + [g for g in city_dict.keys()]))
    for key, value in table_data.items():
        li = [str(key)]
        for k, v in value.items():
            li.append(v)
        response_data.append(li)
    return response_data


def print_current_time(msg=None, previous_time=time.time()):
    t = time.time()
    print("{}: {}, time taken: {} s".format(t, msg, (t - previous_time)))
    return t
