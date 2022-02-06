"""
    Created by tareq on 3/13/17
"""
from collections import OrderedDict

from django.db.models.aggregates import Sum

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.models.base.cache.question_response_cache import QuestionResponseCache
from undp_nuprp.survey.models.entity.answer import Answer

__author__ = 'Tareq'


def get_educational_indicator_pie_chart_data(wards=list(), from_time=None, to_time=None):
    role_wise_queryset = QuestionResponseCache.get_role_based_queryset(
        queryset=QuestionResponseCache.objects.filter()
    ).using(BWDatabaseRouter.get_read_database_name())
    question_responses = role_wise_queryset.filter(
        ref_time__gte=from_time,
        ref_time__lte=to_time,
        question_code='1.8')
    if wards:
        question_responses = question_responses.filter(
            ward_id__in=wards)

    accepted_answers = list(Answer.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
        question__question_code='1.8').values_list('text', flat=True))
    if 'Other' in accepted_answers:
        accepted_answers.remove('Other')
    queryset = question_responses.filter(answer_text__in=accepted_answers).values(
        'answer_text').annotate(count=Sum('survey_count')).order_by('answer_text')
    other_count = question_responses.exclude(answer_text__in=accepted_answers).distinct('pk').count()

    report_data = list()
    for answer in queryset:
        report_data.append({
            'name': answer['answer_text'],
            'y': answer['count']
        })

    report_data.append({
        'name': 'Other',
        'y': other_count
    })
    report = {
        'name': 'Count',
        'data': report_data
    }
    return [report]


def get_educational_indicator_column_chart_data(wards=list(), from_time=None, to_time=None):
    role_wise_queryset = QuestionResponseCache.get_role_based_queryset(
        queryset=QuestionResponseCache.objects.filter()
    ).using(BWDatabaseRouter.get_read_database_name())
    question_responses = role_wise_queryset.filter(
        ref_time__gte=from_time,
        ref_time__lte=to_time,
        question_code='1.8')
    if wards:
        question_responses = question_responses.filter(
            ward_id__in=wards)

    top_six_answers = list(question_responses.filter(question_code='1.8').values('answer_text'). \
                           annotate(count=Sum('survey_count')).order_by('-count').values_list('answer_text',
                                                                                              flat=True)[:6])
    if 'Other' in top_six_answers:
        top_six_answers.remove('Other')
    else:
        top_six_answers = top_six_answers[:5]
    accepted_answers = top_six_answers
    queryset = question_responses.filter(answer_text__in=accepted_answers).values(
        'answer_text', 'city_name').annotate(
        count=Sum('survey_count')).order_by(
        'city_name', 'answer_text')
    other_queryset = question_responses.exclude(answer_text__in=accepted_answers).values(
        'city_name').annotate(
        count=Sum('survey_count')).order_by(
        'city_name')

    city_names = list()
    employment_dict = OrderedDict()
    total_dict = OrderedDict()
    for answer in queryset:
        city_name = answer[
            'city_name']
        employment = answer['answer_text']
        count = answer['count']
        if employment not in employment_dict:
            employment_dict[employment] = {
                'name': employment,
                'data': OrderedDict()
            }
        employment_dict[employment]['data'][city_name] = count
        if city_name not in city_names:
            city_names.append(city_name)
            total_dict[city_name] = 0
        total_dict[city_name] += count
    for answer in other_queryset:
        city_name = answer[
            'city_name']
        employment = 'Other'
        count = answer['count']
        if employment not in employment_dict:
            employment_dict[employment] = {
                'name': employment,
                'data': OrderedDict()
            }
        employment_dict[employment]['data'][city_name] = count
        if city_name not in city_names:
            city_names.append(city_name)
            total_dict[city_name] = 0
        total_dict[city_name] += count

    series = list()
    for key, value in employment_dict.items():
        name = value['name']
        data = list()
        for city in city_names:
            if city in value['data'].keys():
                data.append(value['data'][city] * 100.0 / total_dict[city])
            else:
                data.append(0)
        series.append({
            'name': name,
            'data': data
        })

    return series, city_names


def get_educational_indicator_table_data(wards=list(), from_time=None, to_time=None):
    role_wise_queryset = QuestionResponseCache.get_role_based_queryset(
        queryset=QuestionResponseCache.objects.filter()
    ).using(BWDatabaseRouter.get_read_database_name())
    question_responses = role_wise_queryset.filter(
        ref_time__gte=from_time,
        ref_time__lte=to_time,
        question_code='1.8')
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)
    accepted_answers = list(Answer.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
        question__question_code='1.8').values_list('text', flat=True))
    if 'Other' in accepted_answers:
        accepted_answers.remove('Other')
    queryset = question_responses.filter(answer_text__in=accepted_answers).values('answer_text', 'city_name').order_by(
        'answer_text', 'city_name'
    ).annotate(count=Sum('survey_count'))

    other_queryset = question_responses.order_by('answer__order').exclude(answer_text__in=accepted_answers).values(
        'city_name').annotate(
        count=Sum('survey_count')).order_by(
        'city_name')

    city_dict = OrderedDict()
    for data in queryset:
        city = data.get('city_name') + '(Total)'
        city_percentage = data.get('city_name') + '(%)'
        if city not in city_dict.keys():
            city_dict[city] = 0
            city_dict[city_percentage] = 0
        city_dict[city] += data.get('count')
    for answer in other_queryset:
        city = answer[
                   'city_name'] + '(Total)'
        city_percentage = answer[
                              'city_name'] + '(%)'
        if city not in city_dict.keys():
            city_dict[city] = 0
            city_dict[city_percentage] = 0
        city_dict[city] += answer.get('count')

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
    response_data.append((['Education Attainment of HH Head', ] + [emp for emp in city_dict.keys()]))
    for key, value in table_data.items():
        li = [str(key)]
        for k, v in value.items():
            li.append(v)
        response_data.append(li)
    return response_data
