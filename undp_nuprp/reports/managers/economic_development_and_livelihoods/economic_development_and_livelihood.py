from django.db.models import Sum, Count, When, Case, IntegerField

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.approvals.models import VAWGEarlyMarriagePreventionReporting


def get_established_scc_indicator_table_data(from_time=None, to_time=None):
    queryset = VAWGEarlyMarriagePreventionReporting.objects.using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        queryset = queryset.filter(date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    queryset = queryset.order_by('city__name').values('city__name').annotate(
        established=Sum(Case(When(has_a_committee_been_formed='Yes', then=1),
                             default=0),
                        output_field=IntegerField())
    )

    total = queryset.aggregate(tot=Sum('established'))['tot']
    response_data = [['City', 'Number of SCC established', '% of SCC established']]

    for data in queryset:
        established = data.get('established')
        response_data.append([data.get('city__name') or 'Unassigned', established,
                              '{0:.0f}%'.format(established * 100 / total if total else 0.0)])
    response_data.append(['Total', total, '100%'])

    return response_data


def get_bi_annual_meeting_indicator_table_data(from_time=None, to_time=None):
    queryset = VAWGEarlyMarriagePreventionReporting.objects.using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        queryset = queryset.filter(date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    queryset = queryset.order_by('city__name').values('city__name').annotate(
        established=Sum(Case(When(function_of_scc__any_scc_bi_annual_meeting_held_till_date='Yes', then=1),
                             default=0),
                        output_field=IntegerField())
    )

    total = queryset.aggregate(tot=Sum('established'))['tot']
    response_data = [['City', 'Number of bi-annual meeting held', '% of bi-annual meeting held']]

    for data in queryset:
        established = data.get('established')
        response_data.append([data.get('city__name') or 'Unassigned', established,
                              '{0:.0f}%'.format(established * 100 / total if total else 0.0)])
    response_data.append(['Total', total, '100%'])

    return response_data


def get_initiatives_taken_by_scc_indicator_table_data(from_time=None, to_time=None):
    queryset = VAWGEarlyMarriagePreventionReporting.objects.using(
        BWDatabaseRouter.get_read_database_name()).select_related('city')
    if from_time and to_time:
        queryset = queryset.filter(date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    queryset = queryset.annotate(initiatives=Count('safety_security_initiatives'))

    total = queryset.aggregate(tot=Sum('initiatives'))['tot']
    response_data = [['City', 'Number of initiatives taken', '% of Initiatives taken']]
    city_dict = {}

    for data in queryset:
        city = data.city.name if data.city else 'Unassigned'
        initiatives = data.initiatives
        if city in city_dict:
            city_dict[city] += initiatives
        else:
            city_dict[city] = initiatives

    for city in city_dict.keys():
        response_data.append([city, city_dict[city],
                              '{0:.0f}%'.format(city_dict[city] * 100 / total if total else 0.0)])
    response_data.append(['Total', total, '100%'])

    return response_data
