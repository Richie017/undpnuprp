from collections import OrderedDict

from django.db.models.aggregates import Sum

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


def get_value_of_grantee_indicator_table_data(towns=None):
    if towns is None:
        towns = list()
    grantees = [SEFBusinessGrantee, SEFApprenticeshipGrantee, SEFEducationDropoutGrantee,
                SEFEducationChildMarriageGrantee, SEFNutritionGrantee]

    grand_total_of_grant = 0
    city_wise_grantee_installment_dict = dict()
    city_wise_total = dict()
    grantee_wise_installment_dict = OrderedDict()
    header_row = ['City/Town']

    for grantee in grantees:
        grantee_header = grantee.get_model_meta('route', 'display_name').replace('Grantees', 'Grant')
        header_row += [{
            'column_name': grantee_header,
            'extra_column_name': '{}%'.format(grantee_header),
            'split': 'true'
        }]
        city_wise_grantee_installment_dict[grantee.__name__] = dict()
        grantee_wise_installment_dict[grantee.__name__] = 0

    response_data = []
    city_set = set()

    for grantee in grantees:
        grantee_name = grantee.__name__
        grantee_installment_queryset = grantee.objects.values(
            'pg_member__assigned_to__parent__address__geography__parent__name')
        grantee_wise_installment_queryset = grantee.objects.all()
        if towns:
            grantee_installment_queryset = grantee_installment_queryset.filter(
                pg_member__assigned_to__parent__address__geography__parent__pk__in=towns)
            grantee_wise_installment_queryset = grantee_wise_installment_queryset.filter(
                pg_member__assigned_to__parent__address__geography__parent__pk__in=towns)

        grantee_installment = grantee_installment_queryset.annotate(
            total_installment=Sum('sef_grant_disbursement__instalments__value'))
        grantee_wise_installment = grantee_wise_installment_queryset.aggregate(
            total_installment=Sum('sef_grant_disbursement__instalments__value'))
        grantee_wise_installment_dict[grantee_name] = grantee_wise_installment[
            'total_installment'] if 'total_installment' in grantee_wise_installment and grantee_wise_installment[
            'total_installment'] else 0

        for i, grantee_installment_info in enumerate(grantee_installment):
            total_installment = grantee_installment_info['total_installment']
            city = grantee_installment_info['pg_member__assigned_to__parent__address__geography__parent__name']
            city = city if city else 'Unassigned'
            city_set.add(city)
            if city not in city_wise_total:
                city_wise_total[city] = 0
            city_wise_grantee_installment_dict[grantee_name][city] = total_installment
            city_wise_total[city] += total_installment
            grand_total_of_grant += total_installment

    response_data.append(header_row)
    cities = list(sorted(city_set))
    if 'Unassigned' in cities:
        cities.remove('Unassigned')
        cities.append('Unassigned')  # ensuring Unassigned is at the end
    for city in cities:
        res = [city]
        for grantee in grantees:
            grantee_name = grantee.__name__
            city_wise_grantee_value = city_wise_grantee_installment_dict[grantee_name][city] \
                if city in city_wise_grantee_installment_dict[grantee_name] else 0
            percent_of_grantee_value = city_wise_grantee_value / city_wise_total[city] * 100 if city_wise_total[city] \
                else 0
            res.append('{0:.0f}%'.format(percent_of_grantee_value) + ' (' + thousand_separator(int(city_wise_grantee_value)) + ')')
        response_data.append(res)

    footer_row = ['Total (all cities)']
    for grant_value in grantee_wise_installment_dict.values():
        grantee_percentage = grant_value / grand_total_of_grant * 100 if grand_total_of_grant else 0
        footer_row.append('{0:.0f}% ({1})'.format(grantee_percentage, thousand_separator(int(grant_value))))
    response_data.append(footer_row)
    return response_data


def get_value_of_grantee_indicator_column_chart_data():
    grantees = [SEFBusinessGrantee, SEFApprenticeshipGrantee, SEFEducationDropoutGrantee,
                SEFEducationChildMarriageGrantee, SEFNutritionGrantee]

    grantee_wise_installment_dict = OrderedDict()
    for grantee in grantees:
        grantee_wise_installment_dict[grantee.get_model_meta('route', 'display_name')] = 0

    for grantee in grantees:
        grantee_name = grantee.get_model_meta('route', 'display_name')
        grantee_installment_queryset = grantee.objects.all()

        grantee_installment = grantee_installment_queryset.aggregate(
            total_installment=Sum('sef_grant_disbursement__instalments__value'))
        grantee_wise_installment_dict[grantee_name] = grantee_installment[
            'total_installment'] if 'total_installment' in grantee_installment and grantee_installment[
            'total_installment'] else 0

    data = [
        {
            'name': 'Value of grants distributed',
            'data': list(grantee_wise_installment_dict.values())
        }
    ]

    return data, list(
        map(lambda grant_name: grant_name.replace('Grantees', ''), grantee_wise_installment_dict.keys()))


def get_value_of_grantee_indicator_column_flat_data(towns=None):
    if towns is None:
        towns = list()
    grantees = [SEFBusinessGrantee, SEFApprenticeshipGrantee, SEFEducationDropoutGrantee,
                SEFEducationChildMarriageGrantee, SEFNutritionGrantee]

    total_installment = 0

    for grantee in grantees:
        grantee_installment_queryset = grantee.objects.all()

        if towns:
            grantee_installment_queryset = grantee_installment_queryset.filter(
                pg_member__assigned_to__parent__address__geography__parent__pk__in=towns)

        grantee_installment = grantee_installment_queryset.aggregate(
            total_installment=Sum('sef_grant_disbursement__instalments__value'))['total_installment']
        total_installment += grantee_installment if grantee_installment else 0

    return '<h1 style="font-weight:bold">Total value of grants distributed</h1><div><span style="font-size: 36px;">' \
           + str(thousand_separator(round(total_installment))) + ' (BDT)</span></div>'
