from collections import OrderedDict

from django.db.models import Sum

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.models.cache.pg_member_info_cache import PGMemberInfoCache


def get_hhdependent_members_indicator_column_chart_data(wards=list(), from_time=None, to_time=None):
    question_responses = PGMemberInfoCache.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        question_responses = question_responses.filter(from_time__gte=from_time - 1000, to_time__lte=to_time + 1000)
    if wards:
        question_responses = question_responses.filter(ward_id__in=wards)

    queryset = question_responses.values(
        'city__name'
    ).order_by(
        'city__name'
    ).annotate(
        total_hh_with_children=Sum('household_with_children_count'),
        total_hh_without_children=Sum('household_without_children_count'),
        total_hh_with_adolescent_girl=Sum('household_with_adolescent_girl_count'),
        total_hh_without_adolescent_girl=Sum('household_without_adolescent_girl_count'),
        total_hh_with_disable_member=Sum('household_with_disability_count'),
        total_hh_without_disable_member=Sum('household_without_disability_count')
    )

    city_names = list()
    dependent_dict = dict()
    hh_dependent_constants = ['Children (less than 5 years)', 'Adolescent girls', 'Disabled']
    for dependent_type in hh_dependent_constants:
        dependent_dict[dependent_type] = {
            'name': dependent_type,
            'data': OrderedDict()
        }
    for answer in queryset:
        city_name = answer['city__name']
        total_hh_with_children = answer['total_hh_with_children']
        total_hh_without_children = answer['total_hh_without_children']
        total_hh_with_adolescent_girl = answer['total_hh_with_adolescent_girl']
        total_hh_without_adolescent_girl = answer['total_hh_without_adolescent_girl']
        total_hh_with_disable_member = answer['total_hh_with_disable_member']
        total_hh_without_disable_member = answer['total_hh_without_disable_member']
        if city_name not in city_names:
            city_names.append(city_name)
        for dependent_type in hh_dependent_constants:
            if city_name not in dependent_dict[dependent_type]['data'].keys():
                if dependent_type == 'Children (less than 5 years)':
                    dependent_dict[dependent_type]['data'][city_name] = {
                        'yes': total_hh_with_children, 'no': total_hh_without_children
                    }
                if dependent_type == 'Adolescent girls':
                    dependent_dict[dependent_type]['data'][city_name] = {
                        'yes': total_hh_with_adolescent_girl, 'no': total_hh_without_adolescent_girl
                    }
                if dependent_type == 'Disabled':
                    dependent_dict[dependent_type]['data'][city_name] = {
                        'yes': total_hh_with_disable_member, 'no': total_hh_without_disable_member
                    }

    series = list()
    for key, value in dependent_dict.items():
        name = value['name']
        data = list()
        for city in city_names:
            if city in value['data'].keys():
                total_value = value['data'][city]['yes'] + value['data'][city]['no']
                if total_value > 0:
                    data.append(
                        value['data'][city]['yes'] * 100.0 / (total_value)
                    )
                else:
                    data.append(0)
            else:
                data.append(0)
        series.append({
            'name': name,
            'data': data
        })

    return series, city_names
