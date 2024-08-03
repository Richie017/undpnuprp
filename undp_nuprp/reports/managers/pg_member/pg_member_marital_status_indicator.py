from collections import OrderedDict

from django.db.models import Sum

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.config.constants.pg_survey_constants import PG_MEMBER_MARITAL_STATUS_LIST
from undp_nuprp.reports.models.cache.pg_member_info_cache import PGMemberInfoCache
from undp_nuprp.reports.utils.thousand_separator import thousand_separator


def get_pgmarital_status_indicator_table_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)

    queryset = question_responses.values('city__name', 'marital_status_counts__label').order_by(
        'city__name', 'marital_status_counts__label').annotate(count=Sum('marital_status_counts__count'))

    marital_status_list = PG_MEMBER_MARITAL_STATUS_LIST
    marital_status_dict = OrderedDict()
    for _marital_status in marital_status_list:
        marital_status_dict[_marital_status] = 0

    for data in queryset:
        answer = data.get('marital_status_counts__label')
        count = data.get('count')
        if not answer or not count:
            continue
        if answer not in marital_status_dict.keys():
            marital_status_dict[answer] = 0
        marital_status_dict[answer] += count

    table_data = OrderedDict()
    for data in queryset:
        city = data.get('city__name')
        answer = data.get('marital_status_counts__label')
        count = data.get('count')
        if city is None or answer is None or count is None:
            continue
        if city not in table_data.keys():
            table_data[city] = OrderedDict()
            for c in marital_status_dict.keys():
                table_data[city][c] = 0

        table_data[city][answer] = "{0}".format(count)

    table_data['Total'] = OrderedDict()
    for c in marital_status_dict.keys():
        table_data['Total'][c] = marital_status_dict[c]

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
    for _item in marital_status_dict.keys():
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


def get_pgmarital_status_indicator_pie_chart_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)

    queryset = question_responses.values('marital_status_counts__label').order_by(
        'marital_status_counts__label').annotate(count=Sum('marital_status_counts__count'))

    report_data = list()
    for answer in queryset:
        marital = answer['marital_status_counts__label']
        if not marital:
            continue
        report_data.append({
            'name': marital,
            'y': answer['count']
        })
    report = {
        'name': 'Count',
        'data': report_data
    }
    return [report]
