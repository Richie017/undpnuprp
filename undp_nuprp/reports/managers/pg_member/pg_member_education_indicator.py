from collections import OrderedDict

from django.db.models import Sum

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.config.constants.pg_survey_constants import PG_MEMBER_EDUCATION_ATTAINMENT_LIST
from undp_nuprp.reports.models.cache.pg_member_info_cache import PGMemberInfoCache
from undp_nuprp.reports.utils.thousand_separator import thousand_separator


def get_pg_education_attainment_indicator_pie_chart_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)

    all_answers = list(question_responses.values('education_counts__label').
                       annotate(count=Sum('education_counts__count')).order_by('-count').
                       values_list('education_counts__label', flat=True))

    top_six_answers = all_answers[:6]
    if 'Other' in top_six_answers:
        top_six_answers.remove('Other')
    else:
        top_six_answers = top_six_answers[:5]
    accepted_answers = top_six_answers

    other_answers = list(set(all_answers) - set(accepted_answers))

    queryset = question_responses.filter(education_counts__label__in=accepted_answers).values(
        'education_counts__label').annotate(
        count=Sum('education_counts__count')).order_by('-count', 'education_counts__label')

    other_queryset = question_responses.filter(education_counts__label__in=other_answers). \
        aggregate(count=Sum('education_counts__count'))

    report_data = list()
    for answer in queryset:
        education = answer['education_counts__label']
        if not education:
            continue
        report_data.append({
            'name': education,
            'y': answer['count']
        })

    for k in other_queryset.keys():
        education = 'Other'
        count = other_queryset[k]
        if not education or not count:
            continue
        if count > 0:
            report_data.append({
                'name': education,
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


def get_pg_education_attainment_indicator_table_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)

    queryset = question_responses.values('education_counts__label', 'city__name').annotate(
        count=Sum('education_counts__count')).order_by('-count', 'city__name', 'education_counts__label')

    all_queryset = question_responses.values('city__name', 'education_counts__label').order_by(
        'city__name', 'education_counts__label').annotate(count=Sum('education_counts__count'))

    education_attainment_dict = OrderedDict()
    education_attainment_list = PG_MEMBER_EDUCATION_ATTAINMENT_LIST
    for _education_attainment in education_attainment_list:
        education_attainment_dict[_education_attainment] = 0

    for data in queryset:
        answer = data.get('education_counts__label')
        count = data.get('count')
        if not answer or not count:
            continue
        if answer not in education_attainment_dict.keys():
            education_attainment_dict[answer] = 0
        education_attainment_dict[answer] += count

    table_data = OrderedDict()
    for data in queryset:
        city = data.get(
            'city__name')
        answer = data.get('education_counts__label')
        count = data.get('count')
        if city is None or answer is None or count is None:
            continue
        if city not in table_data.keys():
            table_data[city] = OrderedDict()
            for c in education_attainment_dict.keys():
                table_data[city][c] = 0
        table_data[city][answer] = "{0}".format(count)

    table_data['Total'] = OrderedDict()
    for c in education_attainment_dict.keys():
        table_data['Total'][c] = education_attainment_dict[c]

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
    for _item in education_attainment_dict.keys():
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
