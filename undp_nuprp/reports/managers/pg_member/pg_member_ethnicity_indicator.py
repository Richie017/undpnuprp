from collections import OrderedDict

from django.db.models import Sum

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.config.constants.pg_survey_constants import PG_MEMBER_ETHNICITY_LIST
from undp_nuprp.reports.models.cache.pg_member_info_cache import PGMemberInfoCache
from undp_nuprp.reports.utils.thousand_separator import thousand_separator


def get_pgethnicity_indicator_pie_chart_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)

    all_answers = list(question_responses.values('ethnicity_counts__label').
                       annotate(count=Sum('ethnicity_counts__count')).order_by('-count').
                       values_list('ethnicity_counts__label', flat=True)[:6])

    top_six_answers = all_answers[:6]
    if 'Other' in top_six_answers:
        top_six_answers.remove('Other')
    else:
        top_six_answers = top_six_answers[:5]
    accepted_answers = top_six_answers

    other_answers = list(set(all_answers) - set(accepted_answers))

    queryset = question_responses.filter(ethnicity_counts__label__in=accepted_answers) \
        .values('ethnicity_counts__label').annotate(count=Sum('ethnicity_counts__count')) \
        .order_by('-count', 'ethnicity_counts__label')

    other_queryset = question_responses.filter(ethnicity_counts__label__in=other_answers). \
        aggregate(count=Sum('ethnicity_counts__count'))

    report_data = list()
    for answer in queryset:
        ethnicity = answer['ethnicity_counts__label']
        if not ethnicity:
            continue

        report_data.append({
            'name': ethnicity,
            'y': answer['count']
        })

    for k in other_queryset.keys():
        ethnicity = 'Other'
        count = other_queryset[k]
        if not ethnicity or not count:
            continue
        if count > 0:
            report_data.append({
                'name': ethnicity,
                'y': count
            })
        else:
            report_data.append({
                'name': '',
                'y': 0
            })
    report = {
        'name': 'Count',
        'data': report_data
    }
    return [report]


def get_pgethnicity_indicator_table_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)

    queryset = question_responses.values('ethnicity_counts__label', 'city__name').annotate(
        count=Sum('ethnicity_counts__count')).order_by('-count', 'city__name', 'ethnicity_counts__label')

    all_queryset = question_responses.values('city__name', 'ethnicity_counts__label').order_by(
        'city__name', 'ethnicity_counts__label').annotate(count=Sum('ethnicity_counts__count'))

    ethnicity_list = PG_MEMBER_ETHNICITY_LIST
    ethnicity_dict = OrderedDict()

    for _ethnicity in ethnicity_list:
        ethnicity_dict[_ethnicity] = 0

    for data in queryset:
        answer = data.get('ethnicity_counts__label')
        count = data.get('count')
        if not answer or not count:
            continue

        if answer in ethnicity_dict.keys():
            ethnicity_dict[answer] += count
        else:
            ethnicity_dict['Other'] += count

    table_data = OrderedDict()
    for data in queryset:
        city = data.get('city__name')
        answer = data.get('ethnicity_counts__label')
        count = data.get('count')
        if city is None or answer is None or count is None:
            continue
        if city not in table_data.keys():
            table_data[city] = OrderedDict()
            for c in ethnicity_dict.keys():
                table_data[city][c] = 0

        if answer in table_data[city].keys():
            table_data[city][answer] = count
        else:
            table_data[city]['Other'] += count

    table_data['Total'] = OrderedDict()
    for c in ethnicity_dict.keys():
        table_data['Total'][c] = ethnicity_dict[c]

    city_pg_dict = dict()
    all_cities_pgm = 0
    for data in all_queryset:
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
    for _item in ethnicity_dict.keys():
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
