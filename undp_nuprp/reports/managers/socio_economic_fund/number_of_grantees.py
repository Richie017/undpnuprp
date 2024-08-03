from collections import OrderedDict

from django.db.models.aggregates import Count

from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_apprenticeship_grantee import \
    SEFApprenticeshipGrantee
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_business_grantee import SEFBusinessGrantee
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_education_dropout_grantee import \
    SEFEducationDropoutGrantee
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_education_early_marriage_grantee import \
    SEFEducationChildMarriageGrantee
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_nutrition_grantee import SEFNutritionGrantee
from undp_nuprp.reports.utils.thousand_separator import thousand_separator

__author__ = 'Shuvro'


def get_number_of_grantees_indicator_table_data(towns=None):
    if towns is None:
        towns = list()
    grantees = [SEFBusinessGrantee, SEFApprenticeshipGrantee, SEFEducationDropoutGrantee,
                SEFEducationChildMarriageGrantee, SEFNutritionGrantee]

    header = ['City/Town']
    header += [{'column_name': 'Business Grant', 'extra_column_name': 'Business Grant(%)', 'split': 'true'}]
    header += [
        {'column_name': 'Apprenticeship Grant', 'extra_column_name': 'Apprenticeship Grant(%)', 'split': 'true'}]
    header += [{'column_name': 'Education Grant (Addressing Drop Out)',
                'extra_column_name': 'Education Grant (Addressing Drop Out)(%)',
                'split': 'true'}]
    header += [{'column_name': 'Education Grant (Early Child Marriage)',
                'extra_column_name': 'Education Grant (Early Child Marriage)(%)', 'split': 'true'}]
    header += [{'column_name': 'Nutrition Grant', 'extra_column_name': 'Nutrition Grant(%)', 'split': 'true'}]

    city_wise_total = dict()
    city_wise_grantee_dict = {
        'SEFBusinessGrantee': dict(),
        'SEFApprenticeshipGrantee': dict(),
        'SEFEducationDropoutGrantee': dict(),
        'SEFEducationChildMarriageGrantee': dict(),
        'SEFNutritionGrantee': dict()
    }
    grantee_wise_total = OrderedDict()
    grantee_wise_total['SEFBusinessGrantee'] = 0
    grantee_wise_total['SEFApprenticeshipGrantee'] = 0
    grantee_wise_total['SEFEducationDropoutGrantee'] = 0
    grantee_wise_total['SEFEducationChildMarriageGrantee'] = 0
    grantee_wise_total['SEFNutritionGrantee'] = 0

    response_data = [header]
    city_set = set()
    total_grantee_number = 0

    for grantee in grantees:
        grantee_name = grantee.__name__
        grantee_queryset = grantee.objects
        if towns:
            grantee_queryset = grantee_queryset.filter(
                pg_member__assigned_to__parent__address__geography__parent__pk__in=towns)
        grantee_queryset = grantee_queryset.values(
            'pg_member__assigned_to__parent__address__geography__parent__name').annotate(total=Count('pk'))

        for i, grantee_info in enumerate(grantee_queryset):
            total_gr = grantee_info['total']
            city = grantee_info['pg_member__assigned_to__parent__address__geography__parent__name']
            city = city if city else 'Unassigned'
            city_set.add(city)
            city_wise_grantee_dict[grantee_name][city] = total_gr

            if city not in city_wise_total:
                city_wise_total[city] = 0

            city_wise_total[city] += total_gr
            grantee_wise_total[grantee_name] += total_gr
            total_grantee_number += total_gr

    cities = list(sorted(city_set))
    if 'Unassigned' in cities:
        cities.remove('Unassigned')
        cities.append('Unassigned')  # ensuring Unassigned is at the end

    for city in cities:
        res = [city]
        for grantee in grantees:
            grantee_name = grantee.__name__
            no_of_grantee_in_city = city_wise_grantee_dict[grantee_name][city] if city in city_wise_grantee_dict[
                grantee_name] else 0
            city_total = city_wise_total[city]
            gr_percent = no_of_grantee_in_city / city_total * 100 if city_total else 0
            res.append('{0:.0f}%'.format(gr_percent) + ' (' + thousand_separator(int(no_of_grantee_in_city)) + ')')
        response_data.append(res)

    footer_row = ['Total (all cities)']
    for each_grantee_wise_total in grantee_wise_total.values():
        footer_row.append('{0:.0f}% ({1})'.format(each_grantee_wise_total / total_grantee_number * 100, thousand_separator(int(each_grantee_wise_total))))

    response_data.append(footer_row)
    return response_data


def get_number_of_grantees_indicator_column_chart_data():
    grantees = [SEFBusinessGrantee, SEFApprenticeshipGrantee, SEFEducationDropoutGrantee,
                SEFEducationChildMarriageGrantee, SEFNutritionGrantee]

    grantee_wise_total_dict = OrderedDict()
    for grantee in grantees:
        grantee_wise_total_dict[grantee.get_model_meta('route', 'display_name')] = 0

    for grantee in grantees:
        grantee_name = grantee.get_model_meta('route', 'display_name')
        grantee_queryset = grantee.objects

        total_grantee_dict = grantee_queryset.aggregate(total=Count(
            'pg_member__assigned_to__parent__address__geography__parent'))
        grantee_wise_total_dict[grantee_name] = total_grantee_dict['total'] if 'total' in total_grantee_dict else 0

    data = [
        {
            'name': 'Number of grantee',
            'data': list(grantee_wise_total_dict.values())
        }
    ]

    return data, list(map(lambda grant_name: grant_name.replace('Grantees', ''), grantee_wise_total_dict.keys()))
