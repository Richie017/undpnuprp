from collections import OrderedDict

from django.db.models import Sum

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.models.cache.pg_member_info_cache import PGMemberInfoCache
from undp_nuprp.reports.utils.thousand_separator import thousand_separator

__author__ = "Ziaul Haque"


def get_hh_composition_indicator_table_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)
    queryset = question_responses.values(
        'city__name',
    ).order_by(
        'city__name'
    ).annotate(
        total_male=Sum('household_male_member_count'),
        total_female=Sum('household_female_member_count'),
        total_lactating_mother=Sum('household_lactating_mother_count'),
        total_hh_with_lactating_mother=Sum('household_with_lactating_mother_count'),
        total_children=Sum('household_children_count'),
        total_hh_with_children=Sum('household_with_children_count'),
    )

    city_wise_hh_composition_dict = OrderedDict()
    total_male = 0
    total_female = 0
    total_lactating_mother = 0
    total_hh_with_lactating_mother = 0
    total_children = 0
    total_hh_with_children = 0
    for m in queryset:
        _city = m['city__name']
        if _city not in city_wise_hh_composition_dict.keys():
            city_wise_hh_composition_dict[_city] = {
                'total_male': 0, 'total_female': 0, 'total_lactating_mother': 0, 'total_hh_with_lactating_mother': 0,
                'total_children': 0, 'total_hh_with_children': 0
            }
        city_wise_hh_composition_dict[_city]['total_male'] += m['total_male']
        city_wise_hh_composition_dict[_city]['total_female'] += m['total_female']
        city_wise_hh_composition_dict[_city]['total_lactating_mother'] += m['total_lactating_mother']
        city_wise_hh_composition_dict[_city]['total_hh_with_lactating_mother'] += m['total_hh_with_lactating_mother']
        city_wise_hh_composition_dict[_city]['total_children'] += m['total_children']
        city_wise_hh_composition_dict[_city]['total_hh_with_children'] += m['total_hh_with_children']

        total_male += m['total_male']
        total_female += m['total_female']
        total_lactating_mother += m['total_lactating_mother']
        total_hh_with_lactating_mother += m['total_hh_with_lactating_mother']
        total_children += m['total_children']
        total_hh_with_children += m['total_hh_with_children']

    response_data = list()
    response_data.append((['City Corporation', 'Male', 'Female', 'Number of lactating mothers',
                           'Number of HH with lactating mothers', 'Number of below 5 children',
                           'Number of HH with below 5 children']))
    total_row = ['Total', thousand_separator(int(total_male)), thousand_separator(int(total_female)), thousand_separator(int(total_lactating_mother)), thousand_separator(int(total_hh_with_lactating_mother)),
                 thousand_separator(int(total_children)), thousand_separator(int(total_hh_with_children))]
    for key, value in city_wise_hh_composition_dict.items():
        li = list()
        li.append(str(key))
        li.append(thousand_separator(int(value['total_male'])))
        li.append(thousand_separator(int(value['total_female'])))
        li.append(thousand_separator(int(value['total_lactating_mother'])))
        li.append(thousand_separator(int(value['total_hh_with_lactating_mother'])))
        li.append(thousand_separator(int(value['total_children'])))
        li.append(thousand_separator(int(value['total_hh_with_children'])))
        response_data.append(li)
    response_data.append(total_row)
    return response_data
