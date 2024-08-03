from django.db.models.aggregates import Count
from django.db.models.expressions import Case, When
from django.db.models.fields import IntegerField
from django.db.models.query_utils import Q

from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_business_grantee import SEFBusinessGrantee
from undp_nuprp.nuprp_admin.models.descriptors.business_sector import BusinessSector
from undp_nuprp.reports.utils.thousand_separator import thousand_separator

__author__ = 'Shuvro'


def get_type_of_business_of_business_grantee_table_data(towns=list):
    business_sectors = BusinessSector.objects.all().order_by('name')
    name_of_business_sectors = [business_sector.name for business_sector in business_sectors]

    grantee_queryset = SEFBusinessGrantee.objects.values(
        'pg_member__assigned_to__parent__address__geography__parent__name').order_by(
        'pg_member__assigned_to__parent__address__geography__parent__name')

    sector_wise_business_queryset = SEFBusinessGrantee.objects

    if towns:
        grantee_queryset = grantee_queryset.filter(
            pg_member__assigned_to__parent__address__geography__parent__pk__in=towns)
        sector_wise_business_queryset = sector_wise_business_queryset.filter(
            pg_member__assigned_to__parent__address__geography__parent__pk__in=towns)

    sector_wise_business_info = sector_wise_business_queryset.aggregate(
        total=Count(Case(When(business_sector__isnull=False, then=1))),
        **{
            business_sector.name: Count(
                Case(
                    When(Q(**{'business_sector_id': business_sector.id}), then=1),
                    output_field=IntegerField()
                )) for business_sector in business_sectors
            }
    )

    business_type_by_cities = grantee_queryset.annotate(
        total=Count(Case(When(business_sector__isnull=False, then=1))),
        **{
            business_sector.name: Count(
                Case(
                    When(Q(**{'business_sector_id': business_sector.id}), then=1),
                    output_field=IntegerField()
                )) for business_sector in business_sectors
            }
    )

    response_data = []
    header_row = ['City/Town']
    footer_row = ['Total (all cities)']

    for name_of_business in name_of_business_sectors:
        header_row += [
            {'column_name': name_of_business.replace('&', 'and'),
             'extra_column_name': '{}(%)'.format(name_of_business.replace('&', 'and')), 'split': 'true'}]

    response_data.append(header_row)

    for business_type_by_city in business_type_by_cities:
        city = business_type_by_city['pg_member__assigned_to__parent__address__geography__parent__name']
        city = city if city else 'Unassigned'
        number_of_business = business_type_by_city['total']
        row = [city]
        for name_of_business_sector in name_of_business_sectors:
            number_of_business_by_city = business_type_by_city[name_of_business_sector]
            percent_of_business_by_city = number_of_business_by_city / number_of_business * 100 if number_of_business \
                else 0
            row.append('{0:.0f}%'.format(percent_of_business_by_city) + ' (' + thousand_separator(int(number_of_business_by_city)) + ')')
        response_data.append(row)

    for name_of_business_sector in name_of_business_sectors:
        business_percentage = sector_wise_business_info[name_of_business_sector] / sector_wise_business_info[
            'total'] * 100 if sector_wise_business_info['total'] else 0
        footer_row.append(
            '{0:.0f}% ({1})'.format(business_percentage, thousand_separator(int(sector_wise_business_info[name_of_business_sector])))
        )

    response_data.append(footer_row)

    return response_data


def get_type_of_business_of_business_grantee_pie_chart_data():
    data = []
    business_sectors = BusinessSector.objects.all().order_by('name')
    grantee_queryset = SEFBusinessGrantee.objects

    business_type_by_cities = grantee_queryset.aggregate(
        **{
            business_sector.name: Count(
                Case(
                    When(Q(**{'business_sector_id': business_sector.id}), then=1),
                    output_field=IntegerField()
                )) for business_sector in business_sectors
            }
    )

    for name_of_business, number_of_business in business_type_by_cities.items():
        data.append({
            'name': name_of_business,
            'y': number_of_business
        })

    report = [
        {
            'name': 'Age distribution of grantees',
            'data': data
        }
    ]

    return report
