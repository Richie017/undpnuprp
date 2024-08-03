from collections import OrderedDict

from django.db.models import Sum, Count

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.config.constants.pg_survey_constants import PG_DISABILITY_LABEL_LIST, PG_MEMBER_SURVEY_NAME, \
    HH_DISABLITY_QUESTION_CODE, HH_DISABILITY_LABEL_DICT
from undp_nuprp.reports.models.cache.pg_member_info_cache import PGMemberInfoCache
from undp_nuprp.reports.utils.thousand_separator import thousand_separator
from undp_nuprp.survey.models.indicators.pg_mpi_indicator.mpi_indicator import PGMPIIndicator


def get_hh_head_disability_status_indicator_table_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    total_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
        total_responses = total_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)
        total_responses = total_responses.filter(ward_id__in=wards)

    queryset = question_responses.values('city__name', 'hh_disability_counts__label').order_by(
        'city__name', 'hh_disability_counts__label').annotate(count=Sum('hh_disability_counts__count'),
                                                              total_hh_head=Sum('pg_count'))
    total_queryset = total_responses.values('city__name').annotate(count=Sum('pg_count'))

    head_count = total_queryset.aggregate(count=Sum('hh_gender_counts__count'))

    _disability_labels = PG_DISABILITY_LABEL_LIST

    city_header_dict = OrderedDict()
    for t in total_queryset:
        city = t['city__name']
        city_header_dict[city] = 0

    total_dict = OrderedDict()
    for data in total_queryset:
        city = data.get('city__name')
        if not city:
            continue
        if city not in total_dict.keys():
            total_dict[city] = 0
        total_dict[city] += data.get('count')

    disability_label_dict = OrderedDict()
    for _disability_label in _disability_labels:
        disability_label_dict[_disability_label] = 0

    for data in queryset:
        if data.get('count'):
            answer = data.get('hh_disability_counts__label')
            if answer in disability_label_dict.keys():
                disability_label_dict[answer] += data.get('count')

    table_data = OrderedDict()
    for data in queryset:
        city = data.get('city__name')

        if city is None:
            continue

        total_hh_head = total_dict[city]
        answer = data.get('hh_disability_counts__label')
        count = data.get('count')
        if city not in table_data.keys():
            table_data[city] = OrderedDict()
            table_data[city]['Total Respondent'] = total_hh_head
            for _diability_label in _disability_labels:
                table_data[city][_diability_label] = 0

        if answer and count:
            table_data[city][answer] = "{0:.0f}".format(count)

    response_data = list()
    table_headings = list()
    for _item in disability_label_dict.keys():
        table_headings.append({
            'column_name': str(_item),
            'extra_column_name': str(_item) + "(%)",
            'split': 'true'
        })
    response_data.append((['City/Town', 'Total Respondent', ] + table_headings))
    for key, value in table_data.items():
        li = [str(key)]
        for k, v in value.items():
            if total_dict[key] > 0:
                if k == 'Total Respondent':
                    li.append(thousand_separator(int(v)))
                else:
                    li.append("{0:.0f}%".format(float(v) / total_dict[key] * 100) + ' (' + thousand_separator(int(v)) + ')')
        response_data.append(li)
    if len(response_data) == 1:
        response_data = []
        response_data.append((['City/Town'] + ['No Difficulty']))
        for c in city_header_dict.keys():
            response_data.append(([c] + ['100%' + '(' + thousand_separator(head_count['count']) + ')']))
        return response_data
    else:
        return response_data


def get_hh_head_disability_status_indicator_pie_chart_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMPIIndicator.objects.distinct('survey_response').all()

    total_pg = question_responses.count()
    total_disabled = question_responses.filter(is_head_disabled=True).count()
    report_data = [
        {
            'name': "No difficulty",
            'y': total_pg - total_disabled
        },
        {
            'name': "This includes respondents who have a lot of difficulties <br>"
                    "or cannot do the following functions at all: seeing, <br>"
                    "hearing, walking, remembering, self-care, communicating",
            'y': total_disabled
        }
    ]
    report = {
        'name': 'Count',
        'data': report_data
    }
    return [report]


def get_hh_head_disability_status_indicator_bar_chart_data_old(wards=list(), from_time=None, to_time=None):
    from undp_nuprp.survey.models import QuestionResponse
    _HH_DISABLED_ANSWER_TEXT = ['No difficulty', 'Some difficulty', 'A lot of difficulty', 'Cannot do at all']
    question_responses = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
        section_response__survey_response__survey__name__icontains=PG_MEMBER_SURVEY_NAME,
        question__question_code__in=HH_DISABLITY_QUESTION_CODE,
        answer_text__in=_HH_DISABLED_ANSWER_TEXT
    )
    if from_time and to_time:
        question_responses = question_responses.filter(from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(
            section_response__survey_response__respondent_client__assigned_to__parent__address__geography_id__in=wards)

    queryset = question_responses.values(
        'question__question_code',
        'answer_text'
    ).annotate(
        count=Count('section_response__survey_response__pk', distinct=True)
    )

    total_queryset = question_responses.values(
        'question__question_code'
    ).annotate(
        count=Count('section_response__survey_response__pk', distinct=True)
    )

    total_dict = OrderedDict()
    for data in total_queryset:
        question_code = data.get('question__question_code')
        count = data.get('count')
        if not question_code or not count:
            continue
        if question_code not in total_dict.keys():
            total_dict[question_code] = 0
        total_dict[question_code] += count

    disability_labels = list()
    disability_label_names = list()
    disability_dict = OrderedDict()
    hh_disabled_answer_constants = _HH_DISABLED_ANSWER_TEXT
    for disabled_type in hh_disabled_answer_constants:
        disability_dict[disabled_type] = {
            'name': disabled_type,
            'data': OrderedDict()
        }

    for answer in queryset:
        question_code = answer['question__question_code']
        answer_text = answer['answer_text']
        count = answer['count']

        if question_code not in disability_labels:
            disability_labels.append(question_code)
            disability_label_names.append(HH_DISABILITY_LABEL_DICT[question_code])

        if question_code not in disability_dict[answer_text]['data'].keys():
            disability_dict[answer_text]['data'][question_code] = {
                'count': count
            }

    series = list()
    for key, value in disability_dict.items():
        name = value['name']
        data = list()
        for label in disability_labels:
            _value = 0
            if label in value['data'].keys():
                _v = value['data'][label]['count']
                _value = float(_v) / total_dict[label] * 100
            data.append(_value)
        series.append({
            'name': name,
            'data': data
        })

    return series, disability_label_names


def get_hh_head_disability_status_indicator_bar_chart_data(wards=list(), from_time=None, to_time=None):
    _DISABLED_ANSWER_TEXT = ['No difficulty', 'Some difficulty', 'A lot of difficulty', 'Cannot do at all']
    _disability_label_names = ['Difficulty in Seeing', 'Difficulty in Hearing', 'Difficulty in Walking',
                               'Difficulty in Remebering', 'Difficulty in Self Care', 'Difficulty in Communicating']
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(
            from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)

    difficulty_in_seeing_queryset = question_responses.values(
        'hh_difficulty_in_seeing_counts__label'
    ).annotate(count=Sum('hh_difficulty_in_seeing_counts__count'))

    difficulty_in_seeing_total = question_responses.aggregate(
        count=Sum('hh_difficulty_in_seeing_counts__count')
    )['count']

    difficulty_in_hearing_queryset = question_responses.values(
        'hh_difficulty_in_hearing_counts__label'
    ).annotate(count=Sum('hh_difficulty_in_hearing_counts__count'))

    difficulty_in_hearing_total = question_responses.aggregate(
        count=Sum('hh_difficulty_in_hearing_counts__count')
    )['count']

    difficulty_in_walking_queryset = question_responses.values(
        'hh_difficulty_in_walking_counts__label'
    ).annotate(count=Sum('hh_difficulty_in_walking_counts__count'))

    difficulty_in_walking_total = question_responses.aggregate(
        count=Sum('hh_difficulty_in_walking_counts__count')
    )['count']

    difficulty_in_remembering_queryset = question_responses.values(
        'hh_difficulty_in_remembering_counts__label'
    ).annotate(count=Sum('hh_difficulty_in_remembering_counts__count'))

    difficulty_in_remembering_total = question_responses.aggregate(
        count=Sum('hh_difficulty_in_remembering_counts__count')
    )['count']

    difficulty_in_self_care_queryset = question_responses.values(
        'hh_difficulty_in_self_care_counts__label'
    ).annotate(count=Sum('hh_difficulty_in_self_care_counts__count'))

    difficulty_in_self_care_total = question_responses.aggregate(
        count=Sum('hh_difficulty_in_self_care_counts__count')
    )['count']

    difficulty_in_communicating_queryset = question_responses.values(
        'hh_difficulty_in_communicating_counts__label'
    ).annotate(count=Sum('hh_difficulty_in_communicating_counts__count'))

    difficulty_in_communicating_total = question_responses.aggregate(
        count=Sum('hh_difficulty_in_communicating_counts__count')
    )['count']

    total_dict = OrderedDict()
    disability_dict = OrderedDict()
    disabled_answer_constants = _DISABLED_ANSWER_TEXT
    for disabled_type in disabled_answer_constants:
        disability_dict[disabled_type] = {
            'name': disabled_type,
            'data': OrderedDict()
        }

    disability_type = _disability_label_names[0]
    for q in difficulty_in_seeing_queryset:
        label = q['hh_difficulty_in_seeing_counts__label']
        count = q['count']
        if label is None or count is None:
            continue
        disability_dict[label]['data'][disability_type] = {
            'count': count
        }
    total_dict[disability_type] = difficulty_in_seeing_total

    disability_type = _disability_label_names[1]
    for q in difficulty_in_hearing_queryset:
        label = q['hh_difficulty_in_hearing_counts__label']
        count = q['count']
        if label is None or count is None:
            continue
        disability_dict[label]['data'][disability_type] = {
            'count': count
        }
    total_dict[disability_type] = difficulty_in_hearing_total

    disability_type = _disability_label_names[2]
    for q in difficulty_in_walking_queryset:
        label = q['hh_difficulty_in_walking_counts__label']
        count = q['count']
        if label is None or count is None:
            continue
        disability_dict[label]['data'][disability_type] = {
            'count': count
        }
    total_dict[disability_type] = difficulty_in_walking_total

    disability_type = _disability_label_names[3]
    for q in difficulty_in_remembering_queryset:
        label = q['hh_difficulty_in_remembering_counts__label']
        count = q['count']
        if label is None or count is None:
            continue
        disability_dict[label]['data'][disability_type] = {
            'count': count
        }
    total_dict[disability_type] = difficulty_in_remembering_total

    disability_type = _disability_label_names[4]
    for q in difficulty_in_self_care_queryset:
        label = q['hh_difficulty_in_self_care_counts__label']
        count = q['count']
        if label is None or count is None:
            continue
        disability_dict[label]['data'][disability_type] = {
            'count': count
        }
    total_dict[disability_type] = difficulty_in_self_care_total

    disability_type = _disability_label_names[5]
    for q in difficulty_in_communicating_queryset:
        label = q['hh_difficulty_in_communicating_counts__label']
        count = q['count']
        if label is None or count is None:
            continue
        disability_dict[label]['data'][disability_type] = {
            'count': count
        }
    total_dict[disability_type] = difficulty_in_communicating_total

    series = list()
    for key, value in disability_dict.items():
        name = value['name']
        data = list()
        for label in _disability_label_names:
            _value = 0
            if label in value['data'].keys():
                _v = value['data'][label]['count']
                _value = float(_v) / total_dict[label] * 100
            data.append(_value)
        series.append({
            'name': name,
            'data': data
        })

    return series, _disability_label_names
