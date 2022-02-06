from collections import OrderedDict

from django.db.models import Sum
from django.db.models.aggregates import Count

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.config.constants.pg_survey_constants import HH_DEPRIVATION_INDICATORS, \
    HH_DEPRIVATION_INDICATORS_DESCRIPTIONS
from undp_nuprp.reports.models.cache.pg_member_info_cache import PGMemberInfoCache
from undp_nuprp.reports.utils.thousand_separator import thousand_separator
from undp_nuprp.survey.models.indicators.pg_mpi_indicator.poverty_index import PGPovertyIndex


def get_deprived_pghh_table_data(wards=list(), from_time=None, to_time=None):
    survey_response_domain = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    poverty_index_domain = PGPovertyIndex.get_role_based_queryset(
        queryset=PGPovertyIndex.objects.filter(is_deprived=True)
    ).using(BWDatabaseRouter.get_read_database_name())

    if from_time and to_time:
        survey_response_domain = survey_response_domain.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000
        )
        poverty_index_domain = poverty_index_domain.filter(
            primary_group_member__surveyresponse__survey_time__gte=from_time,
            primary_group_member__surveyresponse__survey_time__lte=to_time
        )
    if wards:
        survey_response_domain = survey_response_domain.filter(ward_id__in=wards)
        poverty_index_domain = poverty_index_domain.filter(
            primary_group_member__surveyresponse__address__geography__parent__parent_id__in=wards
        )

    queryset = poverty_index_domain.values(
        'primary_group_member__assigned_to__parent__address__geography__parent__name',
        'index_no', 'index_name', 'index_description'
    ).annotate(
        count=Count('primary_group_member_id', distinct=True)
    )

    city_queryset = survey_response_domain.values('city__name').annotate(pg_count=Sum('pg_count'))

    all_deprivation_index_names = [x for x in HH_DEPRIVATION_INDICATORS]

    deprivation_indicator_dict = OrderedDict()
    for _deprivation_index in all_deprivation_index_names:
        deprivation_indicator_dict[_deprivation_index] = 0

    for data in queryset:
        index = data.get('index_name')
        if index not in deprivation_indicator_dict.keys():
            deprivation_indicator_dict[index] = 0
        deprivation_indicator_dict[index] += data.get('count')

    city_pg_dict = dict()
    all_cities_pgm = 0

    for c in city_queryset:
        city = c['city__name']
        count = c['pg_count']
        if not city:
            continue
        if city not in city_pg_dict.keys():
            city_pg_dict[city] = 0
        city_pg_dict[city] += count
        all_cities_pgm += count

    for data in queryset:
        city = data.get('primary_group_member__assigned_to__parent__address__geography__parent__name')
        if not city:
            continue
        if city is not None and city not in city_pg_dict.keys():
            city_pg_dict[city] = 0

    table_data = OrderedDict()
    for c in city_queryset:
        city = c['city__name']
        if city not in table_data.keys():
            table_data[city] = OrderedDict()

    table_data['Total'] = OrderedDict()
    for i in all_deprivation_index_names:
        for city in table_data.keys():
            if i not in deprivation_indicator_dict.keys():
                deprivation_indicator_dict[i] = 0
            table_data[city][i] = 0
        table_data['Total'][i] = 0

    for data in queryset:
        city = data.get('primary_group_member__assigned_to__parent__address__geography__parent__name')
        index = data.get('index_name')
        count = data.get('count')
        if city not in table_data.keys():
            table_data[city] = OrderedDict()
            for c in deprivation_indicator_dict.keys():
                table_data[city][c] = 0

        table_data[city][index] = "{0}".format(count)

    for c in deprivation_indicator_dict.keys():
        table_data['Total'][c] = deprivation_indicator_dict[c]

    response_data = list()
    table_headings = list()
    for _item in deprivation_indicator_dict.keys():
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
                    li.append("0%" + ' (' + str(v) + ')')
            else:
                if all_cities_pgm > 0:
                    li.append("{0:.0f}%".format(float(v) / all_cities_pgm * 100) + ' (' + thousand_separator(int(v)) + ')')
                else:
                    li.append("0%" + ' (' + str(v) + ')')
        response_data.append(li)
    return response_data


def get_deprived_pghh_bar_chart_data(wards=list(), from_time=None, to_time=None):
    survey_response_domain = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    poverty_index_domain = PGPovertyIndex.get_role_based_queryset(queryset=PGPovertyIndex.objects.filter(
        is_deprived=True)).using(BWDatabaseRouter.get_read_database_name())

    if from_time and to_time:
        survey_response_domain = survey_response_domain.filter(survey_time__gte=from_time, survey_time__lte=to_time)
        poverty_index_domain = poverty_index_domain.filter(
            primary_group_member__surveyresponse__survey_time__gte=from_time,
            primary_group_member__surveyresponse__survey_time__lte=to_time)
    if wards:
        survey_response_domain = survey_response_domain.filter(address__geography__parent__parent_id__in=wards)
        poverty_index_domain = poverty_index_domain.filter(
            primary_group_member__surveyresponse__address__geography__parent__parent_id__in=wards)

    total_pgm_queryset = survey_response_domain.filter(city__name__isnull=False). \
        aggregate(pg_count=Sum('pg_count'))
    total_pgm_count = total_pgm_queryset['pg_count']

    queryset = poverty_index_domain.values(
        'index_no', 'index_name', 'index_description').annotate(
        count=Count('primary_group_member_id', distinct=True))

    series = [{
        'name': '% of Deprived Household',
        'data': list()
    }]

    all_index_names = [x for x in HH_DEPRIVATION_INDICATORS]
    all_index_description = [x for x in HH_DEPRIVATION_INDICATORS_DESCRIPTIONS]

    description = 0
    for index_no, index in enumerate(all_index_names):
        index = '<div class="hastip" title="{}">{}</div>'.format(all_index_description[description], index)
        all_index_names[index_no] = index
        description += 1

    index_dict = OrderedDict()
    for deprivation in all_index_names:
        index_dict[deprivation] = 0

    for entry in queryset:
        index_name = entry['index_name']
        index_definition = entry['index_description']
        if not index_definition:
            index_definition = index_name
        index_name = '<div class="hastip" title="{}">{}</div>'.format(index_definition, index_name)
        count = round(entry['count'] * 100.0 / total_pgm_count) if total_pgm_count > 0 else 0
        if index_name in index_dict.keys():
            index_dict[index_name] = count

    indices = list()
    for k, v in index_dict.items():
        indices.append(k)
        series[0]['data'].append(v)

    return series, indices
