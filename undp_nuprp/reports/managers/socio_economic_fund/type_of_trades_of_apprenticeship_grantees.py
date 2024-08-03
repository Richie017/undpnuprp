from collections import OrderedDict

from django.db.models.aggregates import Count
from django.db.models.expressions import Case, When
from django.db.models.fields import IntegerField
from django.db.models.query_utils import Q

from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_apprenticeship_grantee import \
    SEFApprenticeshipGrantee
from undp_nuprp.nuprp_admin.models.descriptors.trade_sector import TradeSector
from undp_nuprp.reports.utils.thousand_separator import thousand_separator

__author__ = 'Shuvro'


def get_type_of_trading_of_apprenticeship_grantee_table_data(towns=list):
    trade_sectors = TradeSector.objects.all().order_by('name')
    name_of_trade_sectors = [trade_sector.name for trade_sector in trade_sectors]

    grantee_queryset = SEFApprenticeshipGrantee.objects.values(
        'pg_member__assigned_to__parent__address__geography__parent__name').order_by(
        'pg_member__assigned_to__parent__address__geography__parent__name')

    grantee_total_queryset = SEFApprenticeshipGrantee.objects

    if towns:
        grantee_queryset = grantee_queryset.filter(
            pg_member__assigned_to__parent__address__geography__parent__pk__in=towns)
        grantee_total_queryset = grantee_total_queryset.filter(
            pg_member__assigned_to__parent__address__geography__parent__pk__in=towns)

    trade_type_by_cities = grantee_queryset.annotate(
        total=Count(Case(When(trade_sector__isnull=False, then=1))),
        **{
            trade_sector.name: Count(
                Case(
                    When(Q(**{'trade_sector_id': trade_sector.id}), then=1),
                    output_field=IntegerField()
                )) for trade_sector in trade_sectors
            }
    )
    number_of_trade_by_sector = grantee_total_queryset.aggregate(
        total=Count(Case(When(trade_sector__isnull=False, then=1))),
        **{
            trade_sector.name: Count(
                Case(
                    When(Q(**{'trade_sector_id': trade_sector.id}), then=1),
                    output_field=IntegerField()
                )) for trade_sector in trade_sectors
            }
    )

    response_data = []
    header_row = ['City/Town']
    footer_row = ['Total (all cities)']
    for name_of_trade in name_of_trade_sectors:
        header_row += [
            {'column_name': name_of_trade, 'extra_column_name': '{}(%)'.format(name_of_trade), 'split': 'true'}]

    response_data.append(header_row)

    for trade_type_by_city in trade_type_by_cities:
        city = trade_type_by_city['pg_member__assigned_to__parent__address__geography__parent__name']
        city = city if city else 'Unassigned'
        total_trade_by_city = trade_type_by_city['total']
        row = [city]
        for name_of_business_sector in name_of_trade_sectors:
            number_of_trade_by_city = trade_type_by_city[name_of_business_sector]
            percent_of_trade = number_of_trade_by_city / total_trade_by_city * 100 if total_trade_by_city else 0
            row.append('{0:.0f}%'.format(percent_of_trade) + ' (' + thousand_separator(int(number_of_trade_by_city)) + ')')
        response_data.append(row)

    for name_of_business_sector in name_of_trade_sectors:
        sector_percentage = number_of_trade_by_sector[name_of_business_sector] / number_of_trade_by_sector[
            'total'] * 100 if number_of_trade_by_sector['total'] else 0
        footer_row.append(
            '{0:.0f}% ({1})'.format(sector_percentage, thousand_separator(int(number_of_trade_by_sector[name_of_business_sector])))
        )

    response_data.append(footer_row)

    return response_data


def get_type_of_trading_of_apprenticeship_grantee_pie_chart_data():
    data = []
    trade_sectors = TradeSector.objects.all().order_by('name')
    number_of_trade_sector_count = OrderedDict()

    name_of_trade_sectors = [trade_sector.name for trade_sector in trade_sectors]
    for name_of_trade_sector in name_of_trade_sectors:
        number_of_trade_sector_count[name_of_trade_sector] = 0

    grantee_queryset = SEFApprenticeshipGrantee.objects.order_by(
        'pg_member__assigned_to__parent__address__geography__parent__name')

    trade_type_by_cities = grantee_queryset.aggregate(
        **{
            trade_sector.name: Count(
                Case(
                    When(Q(**{'trade_sector_id': trade_sector.id}), then=1),
                    output_field=IntegerField()
                )) for trade_sector in trade_sectors
            }
    )

    for name_of_business, number_of_business in trade_type_by_cities.items():
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
