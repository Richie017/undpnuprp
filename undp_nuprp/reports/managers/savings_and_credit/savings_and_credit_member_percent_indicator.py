from collections import OrderedDict

from django.db.models import Count

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models import SavingsAndCreditGroup, PrimaryGroupMember
from undp_nuprp.reports.utils.thousand_separator import thousand_separator


def get_scg_member_percent_indicator_flat_data(wards=list(), from_time=None, to_time=None):
    scg_queryset = SavingsAndCreditGroup.objects.all().using(BWDatabaseRouter.get_read_database_name())
    pg_queryset = PrimaryGroupMember.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        scg_queryset = scg_queryset.filter(
            date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
        pg_queryset = pg_queryset.filter(
            date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    if wards:
        scg_queryset = scg_queryset.filter(primary_group__parent__address__geography__pk__in=wards)
        pg_queryset = pg_queryset.filter(assigned_to__parent__address__geography__pk__in=wards)

    queryset = scg_queryset.filter(primary_group__parent__address__geography__parent__name__isnull=False). \
        aggregate(members=Count('members', distinct=True))
    pg_queryset = pg_queryset.filter(assigned_to__parent__address__geography__parent__name__isnull=False). \
        aggregate(pg_count=Count('pk', distinct=True))

    total_members = queryset['members']
    total_pg = pg_queryset['pg_count']
    if total_members is None:
        total_members = 0
    if total_pg > 0:
        return '<h1 style="font-weight:bold">% of SCG Members (all cities)</h1><div><span style="font-size: 36px;">' + \
               "{0:.0f}%".format(float(total_members) / total_pg * 100) + ' (' + thousand_separator(
            total_members) + ')' + '</span></div>'
    else:
        return '<h1 style="font-weight:bold">% of SCG Members (all cities)</h1><div><span style="font-size: 36px;">' + \
               '0' + '</span></div>'


def get_scg_member_percent_indicator_column_chart_data(wards=list(), from_time=None, to_time=None):
    scg_queryset = SavingsAndCreditGroup.objects.all()
    pg_queryset = PrimaryGroupMember.objects.all()

    if from_time:
        scg_queryset = scg_queryset.filter(date_created__gte=from_time)
        pg_queryset = pg_queryset.filter(date_created__gte=from_time)

    if to_time:
        scg_queryset = scg_queryset.filter(date_created__gte=from_time)
        pg_queryset = pg_queryset.filter(date_created__gte=from_time)

    if wards:
        scg_queryset = scg_queryset.filter(primary_group__parent__address__geography__pk__in=wards)
        pg_queryset = pg_queryset.filter(assigned_to__parent__address__geography__pk__in=wards)

    scg_members = scg_queryset.filter(primary_group__parent__address__geography__parent__name__isnull=False).values(
        'primary_group__parent__address__geography__parent__name').annotate(members=Count('members', distinct=True))

    pg_members = pg_queryset.filter(assigned_to__parent__address__geography__parent__name__isnull=False).values(
        'assigned_to__parent__address__geography__parent__name').annotate(members=Count('pk', distinct=True))

    scg_member_percent_dict = OrderedDict()

    for scg_member in scg_members:
        city = scg_member['primary_group__parent__address__geography__parent__name']
        member = scg_member['members']
        scg_member_percent_dict[city] = member

    for pg_member in pg_members:
        city = pg_member['assigned_to__parent__address__geography__parent__name']
        member = pg_member['members']
        if city in scg_member_percent_dict:
            scg_member_percent_dict[city] = float(scg_member_percent_dict[city] / member) * 100

    data = [
        {
            'name': '% of SCG Members',
            'data': list(scg_member_percent_dict.values())
        }
    ]

    return data, list(scg_member_percent_dict.keys())


def get_scg_member_percent_indicator_table_data(wards=list(), from_time=None, to_time=None):
    scg_queryset = SavingsAndCreditGroup.objects.all()
    pg_queryset = PrimaryGroupMember.objects.all()

    if from_time:
        scg_queryset = scg_queryset.filter(date_created__gte=from_time)
        pg_queryset = pg_queryset.filter(date_created__gte=from_time)

    if to_time:
        scg_queryset = scg_queryset.filter(date_created__gte=from_time)
        pg_queryset = pg_queryset.filter(date_created__gte=from_time)

    if wards:
        scg_queryset = scg_queryset.filter(primary_group__parent__address__geography__pk__in=wards)
        pg_queryset = pg_queryset.filter(assigned_to__parent__address__geography__pk__in=wards)

    scg_members = scg_queryset.filter(primary_group__parent__address__geography__parent__name__isnull=False).values(
        'primary_group__parent__address__geography__parent__name').annotate(members=Count('members', distinct=True))

    pg_members = pg_queryset.filter(assigned_to__parent__address__geography__parent__name__isnull=False).values(
        'assigned_to__parent__address__geography__parent__name').annotate(members=Count('pk', distinct=True))

    scg_member_percent_dict = OrderedDict()

    _total_scg_member = 0
    _total_pg_member = 0

    for scg_member in scg_members:
        city = scg_member['primary_group__parent__address__geography__parent__name']
        member = scg_member['members']
        _total_scg_member += member
        scg_member_percent_dict[city] = member

    for pg_member in pg_members:
        city = pg_member['assigned_to__parent__address__geography__parent__name']
        member = pg_member['members']
        _total_pg_member += member
        if city in scg_member_percent_dict:
            scg_member_percent_dict[city] = float(scg_member_percent_dict[city] / member) * 100

    response_data = list()
    response_data.append(['City/Town', '% of SCG Members'])

    for k, v in scg_member_percent_dict.items():
        response_data.append([k, thousand_separator(round(v))])

    response_data.append(['Total (all cities)', round((_total_scg_member / _total_pg_member) * 100)])

    return response_data
