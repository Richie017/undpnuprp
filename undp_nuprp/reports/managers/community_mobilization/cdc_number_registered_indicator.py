from collections import OrderedDict

from django.db.models import Count

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models import PrimaryGroupMember


def get_cdc_number_registered_indicator_table_data(wards=list(), from_time=None, to_time=None):
    pg_member_queryset = PrimaryGroupMember.objects.using(BWDatabaseRouter.get_read_database_name()).all()
    if from_time and to_time:
        pg_member_queryset = pg_member_queryset.filter(
            date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    if wards:
        pg_member_queryset = pg_member_queryset.filter(assigned_to__parent__address__geography__pk__in=wards)
    queryset = pg_member_queryset.values('assigned_to__parent__address__geography__parent__name'). \
        order_by('assigned_to__parent__address__geography__parent__name'). \
        annotate(count=Count('assigned_to__parent_id', distinct=True))

    city_dict = OrderedDict()
    total_cdc = 0
    for data in queryset:
        city = data.get('assigned_to__parent__address__geography__parent__name')
        count = data.get('count')
        if not city or not count:
            continue
        if city is not None and city not in city_dict.keys():
            city_dict[city] = 0
        if city is not None:
            city_dict[city] += data.get('count')
            total_cdc += city_dict[city]

    response_data = list()
    total_row = ['Total (all cities)', str(total_cdc)]
    response_data.append(['City/Town', 'Number of PG Members'])
    for city_name, count in city_dict.items():
        response_data.append([city_name, count])
    response_data.append(total_row)
    return response_data


def get_cdc_number_registered_indicator_flat_data(wards=list(), from_time=None, to_time=None):
    pg_members = PrimaryGroupMember.objects.using(BWDatabaseRouter.get_read_database_name()).all()
    if from_time and to_time:
        pg_members = pg_members.filter(
            date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    if wards:
        pg_members = pg_members.filter(assigned_to__parent__address__geography__pk__in=wards)

    queryset = pg_members.filter(assigned_to__parent__address__geography__parent__isnull=False). \
        aggregate(cdc_count=Count('assigned_to__parent_id', distinct=True))

    total_cdc = queryset['cdc_count']
    if total_cdc is None:
        total_cdc = 0
    return '<h1 style="font-weight:bold">Number of CDCs in which members registered (all cities)</h1><div><span style="font-size: 36px;">' \
           + str(total_cdc) + '</span></div>'
