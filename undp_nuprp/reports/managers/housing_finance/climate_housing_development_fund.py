import calendar
import datetime

from django.db.models import Sum, Case, When, IntegerField

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models import CommunityHousingDevelopmentFund


def get_chdf_status_indicator_table_data(cities=list):
    queryset = CommunityHousingDevelopmentFund.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if cities:
        queryset = queryset.filter(city_id__in=cities)

    now_ = datetime.datetime.now()
    from_ = datetime.datetime(now_.year, now_.month, 1).timestamp() * 1000
    to_ = datetime.datetime(now_.year, now_.month, calendar.mdays[now_.month], 23, 59, 59, 999000).timestamp() * 1000
    queryset = queryset.filter(date_created__gte=from_ - 1000, date_created__lte=to_ + 1000)

    queryset = queryset.order_by('city__name').values('city__name').annotate(
        registered=Sum(Case(When(status_of_chdf_city_wise='CHDF registered', then=1),
                            default=0),
                       output_field=IntegerField()),
        new=Sum(Case(When(status_of_chdf_city_wise='New', then=1),
                     default=0),
                output_field=IntegerField()),
        repaired=Sum(Case(When(status_of_chdf_city_wise='Repair/Upgraded', then=1),
                          default=0),
                     output_field=IntegerField())
    )

    header = ['City', 'CHDF registered', 'New', 'Repair/Upgraded']
    response_data = [header]
    total_registered, total_new, total_repaired = 0, 0, 0

    for data in queryset:
        registered_ = data.get('registered')
        new_ = data.get('new')
        repaired_ = data.get('repaired')
        response_data.append([
            data.get('city__name'), registered_, new_, repaired_
        ])
        total_registered += registered_
        total_new += new_
        total_repaired += repaired_

    footer = ['Total', str(total_registered), str(total_new), str(total_repaired)]
    response_data.append(footer)

    return response_data


def get_implementation_status_indicator_table_data(cities=list):
    queryset = CommunityHousingDevelopmentFund.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if cities:
        queryset = queryset.filter(city_id__in=cities)

    now_ = datetime.datetime.now()
    from_ = datetime.datetime(now_.year, now_.month, 1).timestamp() * 1000
    to_ = datetime.datetime(now_.year, now_.month, calendar.mdays[now_.month], 23, 59, 59, 999000).timestamp() * 1000
    queryset = queryset.filter(date_created__gte=from_ - 1000, date_created__lte=to_ + 1000)

    queryset = queryset.order_by('city__name').values('city__name').annotate(
        con_started=Sum(Case(When(implementation_status='Construction started', then=1),
                             default=0),
                        output_field=IntegerField()),
        strct_completed=Sum(Case(When(implementation_status='Structure completed', then=1),
                                 default=0),
                            output_field=IntegerField()),
        finished=Sum(Case(When(implementation_status='Finished', then=1),
                          default=0),
                     output_field=IntegerField())
    )

    header = ['City', 'Construction started', 'Structure completed', 'Finished']
    response_data = [header]
    total_con, total_strct, total_finished = 0, 0, 0

    for data in queryset:
        con_started_ = data.get('con_started')
        strct_completed_ = data.get('strct_completed')
        finished_ = data.get('finished')
        response_data.append([
            data.get('city__name'), con_started_, strct_completed_, finished_
        ])
        total_con += con_started_
        total_strct += strct_completed_
        total_finished += finished_

    footer = ['Total', str(total_con), str(total_strct), str(total_finished)]
    response_data.append(footer)

    return response_data
