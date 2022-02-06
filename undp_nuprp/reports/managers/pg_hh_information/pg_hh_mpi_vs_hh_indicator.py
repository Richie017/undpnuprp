from collections import OrderedDict

from django.db.models.aggregates import Count

from blackwidow.engine.routers.database_router import BWDatabaseRouter


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

    categories = ['Female headed', 'Male Headed', 'HH head disabled', 'Ethnic minorities']

    total_deprived_female = mpi_indicator_domain.filter(is_female_headed=True, mpi_score__gte=20).count()
    total_rich_female = mpi_indicator_domain.filter(is_female_headed=True, mpi_score__lt=20).count()

    total_deprived_male = mpi_indicator_domain.filter(is_male_headed=True, mpi_score__gte=20).count()
    total_rich_male = mpi_indicator_domain.filter(is_male_headed=True, mpi_score__lt=20).count()

    total_deprived_disabled = mpi_indicator_domain.filter(is_head_disabled=True, mpi_score__gte=20).count()
    total_rich_disabled = mpi_indicator_domain.filter(is_head_disabled=True, mpi_score__lt=20).count()

    total_deprived_minority = mpi_indicator_domain.filter(is_minority=True, mpi_score__gte=20).count()
    total_rich_minority = mpi_indicator_domain.filter(is_minority=True, mpi_score__lt=20).count()

    deprived_female_percent = (total_deprived_female / (total_deprived_female + total_rich_female)) * 100 \
        if (total_deprived_female + total_rich_female) > 0 else 0
    deprived_male_percent = (total_deprived_male / (total_deprived_male + total_rich_male)) * 100 \
        if (total_deprived_male + total_rich_male) > 0 else 0
    deprived_disabled_percent = (total_deprived_disabled / (total_deprived_disabled + total_rich_disabled)) * 100 \
        if (total_deprived_disabled + total_rich_disabled) > 0 else 0
    deprived_minority_percent = (total_deprived_minority / (total_deprived_minority + total_rich_minority)) * 100 \
        if (total_deprived_minority + total_rich_minority) > 0 else 0

    rich_female_percent = (total_rich_female / (total_deprived_female + total_rich_female)) * 100 \
        if (total_deprived_female + total_rich_female) > 0 else 0
    rich_male_percent = (total_rich_male / (total_deprived_male + total_rich_male)) * 100 \
        if (total_deprived_male + total_rich_male) > 0 else 0
    rich_disabled_percent = (total_rich_disabled / (total_deprived_disabled + total_rich_disabled)) * 100 \
        if (total_deprived_disabled + total_rich_disabled) > 0 else 0
    rich_minority_percent = (total_rich_minority / (total_deprived_minority + total_rich_minority)) * 100 \
        if (total_deprived_minority + total_rich_minority) > 0 else 0

    deprived_list = [deprived_female_percent, deprived_male_percent, deprived_disabled_percent,
                     deprived_minority_percent]
    rich_list = [rich_female_percent, rich_male_percent, rich_disabled_percent, rich_minority_percent]

    data = [
        {
            'name': '20 or More',
            'data': deprived_list
        },
        {
            'name': 'Below 20',
            'data': rich_list
        }
    ]

    return data, categories


def get_pghh_mpi_vs_characteristic_indicator_table_data(wards=list(), from_time=None, to_time=None):
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

    deprived_queryset = mpi_indicator_domain.filter(mpi_score__gte=20). \
        values('is_female_headed', 'is_male_headed', 'is_head_disabled', 'is_minority',
               'primary_group_member__assigned_to__parent__address__geography__parent__name'). \
        annotate(count=Count('primary_group_member_id', distinct=True)).order_by(
        'is_female_headed', 'is_male_headed', 'is_head_disabled', 'is_minority'
    )
    all_queryset = mpi_indicator_domain.values(
        'is_female_headed', 'is_male_headed', 'is_head_disabled', 'is_minority',
        'primary_group_member__assigned_to__parent__address__geography__parent__name').annotate(
        count=Count('primary_group_member_id', distinct=True))

    total_city_dict = OrderedDict()
    for data in all_queryset:
        city = data.get('primary_group_member__assigned_to__parent__address__geography__parent__name')
        count = data.get('count')
        if not city or not count:
            continue
        if city not in total_city_dict.keys():
            total_city_dict[city] = OrderedDict()
            total_city_dict[city]['Female Headed'] = 0
            total_city_dict[city]['Male Headed'] = 0
            total_city_dict[city]['Disabled'] = 0
            total_city_dict[city]['Minority'] = 0

        if data['is_female_headed']:
            total_city_dict[city]['Female Headed'] += count
        if data['is_male_headed']:
            total_city_dict[city]['Male Headed'] += count
        if data['is_head_disabled']:
            total_city_dict[city]['Disabled'] += count
        if data['is_minority']:
            total_city_dict[city]['Minority'] += count

    city_dict = OrderedDict()
    for data in deprived_queryset:
        city = data.get('primary_group_member__assigned_to__parent__address__geography__parent__name')
        count = data.get('count')
        if not city or not count:
            continue
        if city not in city_dict.keys():
            city_dict[city] = OrderedDict()
            city_dict[city]['Female Headed'] = 0
            city_dict[city]['Male Headed'] = 0
            city_dict[city]['Disabled'] = 0
            city_dict[city]['Minority'] = 0

        if data['is_female_headed']:
            city_dict[city]['Female Headed'] += count
        if data['is_male_headed']:
            city_dict[city]['Male Headed'] += count
        if data['is_head_disabled']:
            city_dict[city]['Disabled'] += count
        if data['is_minority']:
            city_dict[city]['Minority'] += count

    response_data = list()
    response_data.append((['City/Town', 'Female Headed', 'Male Headed', 'Disabled', 'Minority']))
    for key, value in city_dict.items():
        li = [str(key)]
        for k, v in value.items():
            if total_city_dict[key][k] > 0:
                li.append("{0:.0f}%".format(float(v) / total_city_dict[key][k] * 100))
            else:
                li.append('0%')
        response_data.append(li)
    return response_data
