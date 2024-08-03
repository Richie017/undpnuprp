"""
    Created by tareq on 3/15/17
"""
from django.db.models.aggregates import Count

from blackwidow.engine.routers.database_router import BWDatabaseRouter

__author__ = 'Tareq'


def get_household_mpi_scatter_chart_data(wards=list(), from_time=None, to_time=None):
    from undp_nuprp.survey.models.indicators.mpi_indicator import MPIIndicator
    role_wise_query = MPIIndicator.get_role_based_queryset(queryset=MPIIndicator.objects.filter()).using(
        BWDatabaseRouter.get_read_database_name())
    mpi_indicator_domain = role_wise_query.filter(
        survey_response__survey_time__gte=from_time, survey_response__survey_time__lte=to_time)

    if wards:
        mpi_indicator_domain = mpi_indicator_domain.filter(
            survey_response__address__geography__parent__parent_id__in=wards)

    # do the group by SQL syntax with city name and counting household_ids
    city_wise_queryset = mpi_indicator_domain.values(
        'household__address__geography__parent__parent__parent__name'
    ).annotate(
        count=Count('household_id', distinct=True)
    )

    # create dictionary for holding cities and their own household counts
    city_household_dict = dict()
    for survey_data in city_wise_queryset:
        city_name = survey_data['household__address__geography__parent__parent__parent__name']
        household_count = survey_data['count']

        if city_name not in city_household_dict.keys():
            # When a new city will come, it'll be added here
            city_household_dict[city_name] = {
                'household_count': household_count
            }

    queryset = mpi_indicator_domain.values(
        'mpi_score', 'household__address__geography__parent__parent__parent__name'
    ).annotate(
        count=Count('household_id', distinct=True)
    ).order_by(
        'household__address__geography__parent__parent__parent__name'
    )

    mpi_dict = dict()
    for entry in queryset:
        city_name = entry['household__address__geography__parent__parent__parent__name']
        mpi_score = entry['mpi_score']
        count = entry['count'] * 100.0 / city_household_dict.get(city_name, '').get('household_count', 0)
        if city_name not in mpi_dict:
            mpi_dict[city_name] = {
                'name': city_name,
                'data': list()
            }
        mpi_dict[city_name]['data'].append([mpi_score, count])

    return list(mpi_dict.values())


def get_household_mpi_column_chart_data(wards=list(), from_time=None, to_time=None):
    from undp_nuprp.survey.models.indicators.mpi_indicator import MPIIndicator
    role_wise_query = MPIIndicator.get_role_based_queryset(queryset=MPIIndicator.objects.filter()).using(
        BWDatabaseRouter.get_read_database_name())
    mpi_indicator_domain = role_wise_query.filter(
        survey_response__survey_time__gte=from_time, survey_response__survey_time__lte=to_time)
    if wards:
        mpi_indicator_domain = mpi_indicator_domain.filter(
            survey_response__address__geography__parent__parent_id__in=wards)

    queryset = mpi_indicator_domain.values(
        'mpi_score', 'household__address__geography__parent__parent__parent__name'
    ).annotate(
        count=Count('household_id', distinct=True)
    ).order_by(
        'household__address__geography__parent__parent__parent__name'
    )

    mpi_dict = dict()
    city_list = list()
    total_dict = dict()

    for entry in queryset:
        city_name = entry[
            'household__address__geography__parent__parent__parent__name']
        mpi_score = entry['mpi_score']
        count = entry['count']

        if city_name not in mpi_dict.keys():
            mpi_dict[city_name] = {
                'deprived': 0,
                'rich': 0
            }
        if mpi_score < 30:
            mpi_dict[city_name]['rich'] += count
        else:
            mpi_dict[city_name]['deprived'] += count

        if city_name not in city_list:
            city_list.append(city_name)
            total_dict[city_name] = 0
        total_dict[city_name] += count

    deprived_list = [(mpi_dict[c]['deprived'] * 100.0 / total_dict[c]) for c in city_list]
    rich_list = [(mpi_dict[c]['rich'] * 100.0 / total_dict[c]) for c in city_list]

    data = [
        {
            'name': '30 or More',
            'data': deprived_list
        },
        {
            'name': 'Below 30',
            'data': rich_list
        }
    ]

    return data, city_list
