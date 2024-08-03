from datetime import datetime
from django.db.models import Sum
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models import CDCAssessment

__author__ = 'Kaikobud'


def get_cdc_performance_indicator_table_data_1(year=None):
    from_time = int(
        datetime.now().replace(year=int(year), month=1, day=1, hour=00, minute=00, second=00).timestamp() * 1000)
    to_time = int(
        datetime.now().replace(year=int(year), month=12, day=31, hour=23, minute=59, second=59).timestamp() * 1000)
    queryset = CDCAssessment.objects.filter(date_created__gte=from_time, date_created__lte=to_time). \
        using(BWDatabaseRouter.get_read_database_name())
    queryset = queryset.order_by('city__name').values('city__name').annotate(
        sum_number_of_cdc=Sum('number_of_cdc'),
        sum_fully_effective=Sum('fully_effective'),
        sum_moderately_effective=Sum('moderately_effective'),
        sum_weak=Sum('weak'),
        sum_very_weak=Sum('very_weak')
    )

    response_data = [['City', 'Number of CDC',
                      {'column_name': 'No of CDCs Fully effective',
                       'extra_column_name': 'No of CDCs Fully effective(%)',
                       'split': 'true'},
                      {'column_name': 'No of  CDCs Moderately Effective',
                       'extra_column_name': 'No of  CDCs Moderately Effective(%)',
                       'split': 'true'},
                      {'column_name': 'No of CDCs Weak',
                       'extra_column_name': 'No of CDCs Weak(%)',
                       'split': 'true'},
                      {'column_name': 'No of CDCs Very Weak',
                       'extra_column_name': 'No of CDCs Very Weak(%)',
                       'split': 'true'}
                      ]]

    for data in queryset:
        sum_of_cdc = data.get('sum_number_of_cdc') or 0
        c1 = data.get('sum_fully_effective') or 0
        c2 = data.get('sum_moderately_effective') or 0
        c3 = data.get('sum_weak') or 0
        c4 = data.get('sum_very_weak') or 0
        response_data.append([data.get('city__name') or 'Unassigned', sum_of_cdc,
                              '{0:.0f}%'.format(c1 * 100 / sum_of_cdc if sum_of_cdc else 0.0) + ' (' + str(c1) + ')',
                              '{0:.0f}%'.format(c2 * 100 / sum_of_cdc if sum_of_cdc else 0.0) + ' (' + str(c2) + ')',
                              '{0:.0f}%'.format(c3 * 100 / sum_of_cdc if sum_of_cdc else 0.0) + ' (' + str(c3) + ')',
                              '{0:.0f}%'.format(c4 * 100 / sum_of_cdc if sum_of_cdc else 0.0) + ' (' + str(c4) + ')',
                              ])

    return response_data
