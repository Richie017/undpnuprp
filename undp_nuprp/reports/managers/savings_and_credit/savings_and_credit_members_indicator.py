from collections import OrderedDict

from django.db.models import Count

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models import SavingsAndCreditGroup
from undp_nuprp.reports.utils.thousand_separator import thousand_separator


__author__ = 'Farina', 'Shuvro'


def get_scg_member_number_indicator_flat_data(wards=list(), from_time=None, to_time=None):
    scg_queryset = SavingsAndCreditGroup.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        scg_queryset = scg_queryset.filter(
            date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    if wards:
        scg_queryset = scg_queryset.filter(primary_group__parent__address__geography__pk__in=wards)

    queryset = scg_queryset.filter(primary_group__parent__address__geography__parent__name__isnull=False). \
        aggregate(members=Count('members', distinct=True))

    total_members = queryset['members']
    if total_members is None:
        total_members = 0
    return '<h1 style="font-weight:bold">Number of SCG members (all cities)</h1><div><span style="font-size: 36px;">' \
           + str(thousand_separator(total_members)) + '</span></div>'


def get_scg_member_number_indicator_table_data(wards=list(), from_time=None, to_time=None):
    scg_queryset = SavingsAndCreditGroup.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        scg_queryset = scg_queryset.filter(
            date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    if wards:
        scg_queryset = scg_queryset.filter(primary_group__parent__address__geography__pk__in=wards)
    queryset = scg_queryset.values(
        'primary_group__parent__address__geography__parent__name').order_by(
        'primary_group__parent__address__geography__parent__name').annotate(count=Count('members', distinct=True))

    city_dict = OrderedDict()
    total_pg = 0
    for data in queryset:
        city = data.get('primary_group__parent__address__geography__parent__name')
        count = data.get('count')
        if not city or not count:
            continue
        if city is not None and city not in city_dict.keys():
            city_dict[city] = 0
        if city is not None:
            city_dict[city] += data.get('count')
            total_pg += city_dict[city]

    response_data = list()
    total_row = ['Total (all cities)', thousand_separator(total_pg)]
    response_data.append(['City/Town', 'Number of SCG Members'])
    for city_name, count in city_dict.items():
        response_data.append([city_name, thousand_separator(count)])
    response_data.append(total_row)
    return response_data


def get_scg_member_number_indicator_column_chart_data(wards=list(), from_time=None, to_time=None):
    scg_queryset = SavingsAndCreditGroup.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        scg_queryset = scg_queryset.filter(
            date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    if wards:
        scg_queryset = scg_queryset.filter(primary_group__parent__address__geography__pk__in=wards)
    queryset = scg_queryset.values(
        'primary_group__parent__address__geography__parent__name').order_by(
        'primary_group__parent__address__geography__parent__name').annotate(count=Count('members', distinct=True))

    city_dict = OrderedDict()
    total_pg = 0
    for data in queryset:
        city = data.get('primary_group__parent__address__geography__parent__name')
        count = data.get('count')
        if not city or not count:
            continue
        if city is not None and city not in city_dict.keys():
            city_dict[city] = 0
        if city is not None:
            city_dict[city] += data.get('count')
            total_pg += city_dict[city]

    data = [
        {
            'name': 'SCG member',
            'data': list(city_dict.values())
        }
    ]

    return data, list(city_dict.keys())