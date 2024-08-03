from collections import OrderedDict

from django.db.models.aggregates import Count, Avg
from django.db.models.fields import IntegerField
from django.db.models.functions.base import Cast

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.survey.models.response.question_response import QuestionResponse

__author__ = "Shama"


def get_hhdependent_members_indicator_column_chart_data(wards=list(), from_time=None, to_time=None):
    members_dict = {
        '4.4.7': 'Children (less than 5 years)',
        '4.4.8': 'Adolescent girls',
        '4.4.9': 'Disabled'
    }
    role_wise_queryset = QuestionResponse.get_role_based_queryset(
        queryset=QuestionResponse.objects.filter(
            section_response__survey_response__survey__name='PG Member Survey Questionnaire')
    ).using(BWDatabaseRouter.get_read_database_name())
    question_responses = role_wise_queryset.filter(question__question_code__in=list(members_dict.keys()))
    if wards:
        question_responses = question_responses.filter(
            section_response__survey_response__respondent_client__assigned_to__parent__address__geography_id__in=wards)
    queryset = question_responses.values(
        'question__question_code', 'answer_text',
        'section_response__survey_response__respondent_client__assigned_to__parent__address__geography__parent__name').order_by(
        'section_response__survey_response__respondent_client__assigned_to__parent__address__geography__parent__name').annotate(
        count=Count('section_response__survey_response_id', distinct=True))
    queryset = QuestionResponse.get_cached_queryset(queryset=queryset)

    city_names = list()
    dependent_dict = dict()
    for answer in queryset:
        city_name = answer[
            'section_response__survey_response__respondent_client__assigned_to__parent__address__geography__parent__name']
        dependent_type = members_dict[answer['question__question_code']]
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


def get_pghh_mpi_vs_characteristic_indicator_column_chart_data(wards=list(), from_time=None, to_time=None):
    from undp_nuprp.survey.models.indicators.pg_mpi_indicator.mpi_indicator import PGMPIIndicator
    mpi_indicator_domain = PGMPIIndicator.get_role_based_queryset(queryset=PGMPIIndicator.objects.filter(
        survey_response__survey__name='PG Member Survey Questionnaire')).using(
        BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        mpi_indicator_domain = mpi_indicator_domain.filter(
            survey_response__survey_time__gte=from_time, survey_response__survey_time__lte=to_time
        )
    if wards:
        mpi_indicator_domain = mpi_indicator_domain.filter(
            survey_response__address__geography__parent__parent_id__in=wards)

    mpi_domain = PGMPIIndicator.get_cached_queryset(queryset=mpi_indicator_domain)

    categories = ['Female headed households', 'Household head is disabled', 'Ethnic minorities', 'Other Households']

    avg_female = mpi_domain.filter(is_female_headed=True).aggregate(Avg('mpi_score'))['mpi_score__avg']
    avg_disabled = mpi_domain.filter(is_head_disabled=True).aggregate(Avg('mpi_score'))['mpi_score__avg']
    avg_minority = mpi_domain.filter(is_minority=True).aggregate(Avg('mpi_score'))['mpi_score__avg']
    avg_other = mpi_domain.filter(
        is_female_headed=False, is_head_disabled=False, is_minority=False).aggregate(Avg('mpi_score'))['mpi_score__avg']

    data = [
        {
            'name': 'Avg. MPI Score',
            'data': [
                avg_female if avg_female else 0,
                avg_disabled if avg_disabled else 0,
                avg_minority if avg_minority else 0,
                avg_other if avg_other else 0,
            ]
        }
    ]
    return data, categories


def get_hh_composition_indicator_table_data(wards=list(), from_time=None, to_time=None):
    member_responses = QuestionResponse.objects.filter(
        section_response__survey_response__survey__name__icontains='PG Member Survey Questionnaire',
        question__question_code__in=['4.4.2', '4.4.3', '4.4.9.1', '4.4.5.1', '4.4.6.1', '4.4.7.1', '4.4.8.1']).using(
        BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        member_responses = member_responses.filter(
            section_response__survey_response__survey_time__gte=from_time,
            section_response__survey_response__survey_time__lte=to_time)

    if wards:
        member_responses = member_responses.filter(
            section_response__survey_response__respondent_client__assigned_to__parent__address__geography_id__in=wards)
    queryset = member_responses.values('answer_text', 'question__question_code',
                                       'section_response__survey_response__respondent_client__assigned_to__parent__address__geography__parent__name').order_by(
        'section_response__survey_response__respondent_client__assigned_to__parent__address__geography__parent__name'
    ).annotate(members=Cast('answer_text', IntegerField()),
               count=Count('section_response__survey_response_id', distinct=True))

    queryset = QuestionResponse.get_cached_queryset(queryset=queryset)

    city_dict = OrderedDict()
    for data in queryset:
        answer = data.get('answer_text')
        question_code = data.get('question__question_code')
        hh = ''
        if question_code == '4.4.2':
            answer = 'Male'
        elif question_code == '4.4.3':
            answer = 'Female'
        elif question_code == '4.4.9.1':
            answer = 'Disabled'
            hh = 'Number of HH with disabled'
        elif question_code == '4.4.5.1':
            answer = 'Number of Pregnant Woman'
            hh = 'Number of HH with Pregnant Woman'
        elif question_code == '4.4.6.1':
            answer = 'Number of lactating mothers'
            hh = 'Number of HH with lactating mothers'
        elif question_code == '4.4.7.1':
            answer = 'Number of below 5 children'
            hh = 'Number of HH with below 5 children'
        elif question_code == '4.4.8.1':
            answer = 'Number of adolescent girls'
            hh = 'Number of HH with adolescent girls'
        if answer not in city_dict.keys():
            city_dict[answer] = 0
        if hh not in city_dict.keys() and hh:
            city_dict[hh] = 0
        city_dict[answer] += data.get('members')
        if hh:
            city_dict[hh] += data.get('count')

    table_data = OrderedDict()
    for data in queryset:
        city = data.get(
            'section_response__survey_response__respondent_client__assigned_to__parent__address__geography__parent__name')
        answer = data.get('answer_text')
        hh = ''
        question_code = data.get('question__question_code')
        if question_code == '4.4.2':
            answer = 'Male'
        elif question_code == '4.4.3':
            answer = 'Female'
        elif question_code == '4.4.9.1':
            answer = 'Disabled'
            hh = 'Number of HH with disabled'
        elif question_code == '4.4.5.1':
            answer = 'Number of Pregnant Woman'
            hh = 'Number of HH with Pregnant Woman'
        elif question_code == '4.4.6.1':
            answer = 'Number of lactating mothers'
            hh = 'Number of HH with lactating mothers'
        elif question_code == '4.4.7.1':
            answer = 'Number of below 5 children'
            hh = 'Number of HH with below 5 children'
        elif question_code == '4.4.8.1':
            answer = 'Number of adolescent girls'
            hh = 'Number of HH with adolescent girls'
        count = data.get('members')
        survey = data.get('count')
        if city not in table_data.keys():
            table_data[city] = OrderedDict()
            for c in city_dict.keys():
                table_data[city][c] = 0

        table_data[city][answer] += count
        if hh:
            table_data[city][hh] += survey
    table_data['Total'] = OrderedDict()
    for c in city_dict.keys():
        table_data['Total'][c] = city_dict[c]

    response_data = list()
    response_data.append((['City Corporation', ] + [g for g in city_dict.keys()]))
    for key, value in table_data.items():
        li = [str(key)]
        for k, v in value.items():
            li.append(v)
        response_data.append(li)
    return response_data
