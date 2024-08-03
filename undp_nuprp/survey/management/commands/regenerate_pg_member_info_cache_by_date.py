"""
    Created by Shuvro on 30/07/19
"""
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from undp_nuprp.reports.models.cache.pg_member_info_cache import PGMemberInfoCache

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            _date_list = ["2018,3,21", "2018,5,11", "2018,9,21", "2018,9,24", "2019,4,21", "2019,4,23",
                          "2019,4,24", "2019,4,25", "2019,4,29", "2019,4,30", "2019,5,2", "2019,5,5",
                          "2019,5,6", "2019,5,7", "2019,5,8", "2019,5,9", "2019,5,12", "2019,5,13",
                          "2019,5,14", "2019,5,15", "2019,5,16", "2019,5,19", "2019,5,20", "2019,5,23",
                          "2019,5,24", "2019,5,25", "2019,6,5", "2019,6,7", "2019,6,9", "2019,6,12",
                          "2019,6,14", "2019,6,15", "2019,6,17", "2019,6,18", "2019,6,19", "2019,6,25",
                          "2019,6,27", "2019,6,30", "2019,7,6", "2019,7,7", "2019,7,8", "2019,7,10",
                          "2019,7,11", "2019,7,12", "2019,7,14", "2019,7,16", "2019,7,23", "2019,7,29"]

            for date_string in _date_list:
                dt = datetime.strptime(date_string, "%Y,%m,%d").replace(hour=12)
                print('Regenerating PG member cache for date {}'.format(dt))

                from_dt = dt.replace(hour=0, minute=0, second=0).timestamp() * 1000
                to_dt = dt.replace(hour=23, minute=59, second=59).timestamp() * 1000
                timestamp = dt.timestamp() * 1000

                # delete PG member infor cache for the day
                PGMemberInfoCache.objects.filter(from_time__lt=timestamp, to_time__gt=timestamp).delete()
                PGMemberInfoCache.cache_intervaled_report(from_time=from_dt, to_time=to_dt)
                print('Successfully generated')
