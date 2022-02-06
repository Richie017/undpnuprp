"""
    Created by tareq on 3/15/17
"""
from collections import OrderedDict

from django.db.models.aggregates import Count

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.survey.models.indicators.poverty_index import PovertyIndex
from undp_nuprp.survey.models.response.survey_response import SurveyResponse

__author__ = 'Tareq'


def get_deprived_household_column_chart_data(wards=list(), from_time=None, to_time=None):
    role_wise_query = SurveyResponse.get_role_based_queryset(queryset=SurveyResponse.objects.filter()).using(
        BWDatabaseRouter.get_read_database_name())
    poverty_role_wise_query = PovertyIndex.get_role_based_queryset(queryset=PovertyIndex.objects.filter()).using(
        BWDatabaseRouter.get_read_database_name())

    survey_response_domain = role_wise_query.filter(survey_time__gte=from_time, survey_time__lte=to_time)
    poverty_index_domain = poverty_role_wise_query.filter(
        is_deprived=True, household__surveyresponse__survey_time__gte=from_time,
        household__surveyresponse__survey_time__lte=to_time)
    if wards:
        survey_response_domain = survey_response_domain.filter(address__geography__parent__parent_id__in=wards)
        poverty_index_domain = poverty_index_domain.filter(
            household__surveyresponse__address__geography__parent__parent_id__in=wards)

    total_household_count = survey_response_domain.distinct('respondent_unit_id').count()

    queryset = poverty_index_domain.values(
        'index_no', 'index_name', 'index_description',
        'household__address__geography__parent__parent__parent__name').annotate(
        count=Count('household_id', distinct=True))

    index_names = list()
    index_dict = dict()
    for entry in queryset:
        city_name = entry[
            'household__address__geography__parent__parent__parent__name']
        index_name = entry['index_name']
        index_definition = entry['index_description']
        if not index_definition:
            index_definition = index_name
        index_name = '<div class="hastip" title="{}">{}</div>'.format(index_definition, index_name)
        count = entry['count'] * 100.0 / total_household_count if total_household_count else 0
        if city_name not in index_dict:
            index_dict[city_name] = {
                'name': city_name,
                'data': list()
            }
        index_dict[city_name]['data'].append(count)
        if index_name not in index_names:
            index_names.append(index_name)

    return list(index_dict.values()), index_names


def get_deprived_household_bar_chart_data(wards=list(), from_time=None, to_time=None):
    role_wise_query = SurveyResponse.get_role_based_queryset(queryset=SurveyResponse.objects.filter()).using(
        BWDatabaseRouter.get_read_database_name())
    poverty_role_wise_query = PovertyIndex.get_role_based_queryset(queryset=PovertyIndex.objects.filter()).using(
        BWDatabaseRouter.get_read_database_name())

    survey_response_domain = role_wise_query.filter(survey_time__gte=from_time, survey_time__lte=to_time)
    poverty_index_domain = poverty_role_wise_query.filter(
        is_deprived=True, household__surveyresponse__survey_time__gte=from_time,
        household__surveyresponse__survey_time__lte=to_time)
    if wards:
        survey_response_domain = survey_response_domain.filter(address__geography__parent__parent_id__in=wards)
        poverty_index_domain = poverty_index_domain.filter(
            household__surveyresponse__address__geography__parent__parent_id__in=wards)

    total_household_count = survey_response_domain.distinct('respondent_unit_id').count()

    queryset = poverty_index_domain.values(
        'index_no', 'index_name', 'index_description').annotate(
        count=Count('household_id', distinct=True))

    index_names = list()
    series = [{
        'name': '% of Deprived Household',
        'data': list()
    }]
    for entry in queryset:
        index_name = entry['index_name']
        index_definition = entry['index_description']
        if not index_definition:
            index_definition = index_name
        index_name = '<div class="hastip" title="{}">{}</div>'.format(index_definition, index_name)
        count = entry['count'] * 100.0 / total_household_count if total_household_count else 0
        series[0]['data'].append(count)
        if index_name not in index_names:
            index_names.append(index_name)

    return series, index_names


def get_deprived_household_table_data(wards=list(), from_time=None, to_time=None):
    role_wise_query = SurveyResponse.get_role_based_queryset(queryset=SurveyResponse.objects.filter()).using(
        BWDatabaseRouter.get_read_database_name())
    poverty_role_wise_query = PovertyIndex.get_role_based_queryset(queryset=PovertyIndex.objects.filter()).using(
        BWDatabaseRouter.get_read_database_name())

    survey_response_domain = role_wise_query.filter(survey_time__gte=from_time, survey_time__lte=to_time)
    poverty_index_domain = poverty_role_wise_query.filter(
        is_deprived=True, household__surveyresponse__survey_time__gte=from_time,
        household__surveyresponse__survey_time__lte=to_time)
    if wards:
        survey_response_domain = survey_response_domain.filter(address__geography__parent__parent_id__in=wards)
        poverty_index_domain = poverty_index_domain.filter(
            household__surveyresponse__address__geography__parent__parent_id__in=wards)

    total_household_count = survey_response_domain.distinct('respondent_unit_id').count()

    queryset = poverty_index_domain.values('household__address__geography__parent__parent__parent__name',
                                           'index_no', 'index_name', 'index_description').annotate(
        count=Count('household_id', distinct=True))

    city_dict = OrderedDict()
    for data in queryset:
        city = data.get('household__address__geography__parent__parent__parent__name') + '(Total)'
        city_percentage = data.get('household__address__geography__parent__parent__parent__name') + '(%)'
        if city not in city_dict.keys():
            city_dict[city] = 0
            city_dict[city_percentage] = 0
        city_dict[city] += data.get('count')

    table_data = OrderedDict()
    for data in queryset:
        city = data.get('household__address__geography__parent__parent__parent__name') + '(Total)'
        city_percentage = data.get('household__address__geography__parent__parent__parent__name') + '(%)'
        index = data.get('index_name')
        count = data.get('count')
        if index not in table_data.keys():
            table_data[index] = OrderedDict()
            for c in city_dict.keys():
                table_data[index][c] = 'N/A'

        table_data[index][city] = "{0}".format(count)
        table_data[index][city_percentage] = "{0}%".format(
            float("{0:.2f}".format(((count / total_household_count) * 100))))

    response_data = list()
    response_data.append((['Deprivation by Indicator', ] + [i for i in city_dict.keys()]))
    for key, value in table_data.items():
        li = [str(key)]
        for k, v in value.items():
            li.append(v)
        response_data.append(li)
    return response_data
