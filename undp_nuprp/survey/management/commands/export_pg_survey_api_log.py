import json
import os

from django.core.management import BaseCommand
from django.db.models import Max

from blackwidow.core.models import *
from settings import STATIC_ROOT

__author__ = 'Ziaul Haque'


class Command(BaseCommand):
    help = "parameter in format 150805"

    def add_arguments(self, parser):
        parser.add_argument('log_id', nargs='+', type=int)

    def handle(self, *args, **options):
        log_id = options['log_id'][0]

        file_path = os.path.join(STATIC_ROOT, 'data/')
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        filename = file_path + 'pg_survey_api_log.csv'
        if log_id == 0:
            csv = open(filename, "w", encoding='utf-8')
            skip_header = False
        else:
            csv = open(filename, "a", encoding='utf-8')
            skip_header = True

        if not skip_header:
            csv.write("API Log ID,Survey Response Tsync ID\n")

        offset = 0
        limit = 10000

        queryset = ApiCallLog.objects.filter(
            request_type='POST', url__icontains='survey-response',
            pk__gt=log_id, response_data='201 Created', date_created__gte=1519102976685
        ).order_by('date_created')

        max_id = queryset.aggregate(Max('pk'))['pk__max']
        max_processed_id = 0
        while max_processed_id < max_id:
            api_logs = queryset[offset:limit]
            _h = 0
            for api_log in api_logs:
                _log_id = api_log.pk
                max_processed_id = _log_id
                if _h % 2000 == 0:
                    print('{}'.format(_h, ))
                _h += 1
                body = api_log.request_body
                if body:
                    try:
                        body = json.loads(body)
                    except:
                        continue
                    tsync_id = body['tsync_id']
                    csv.write('{},{}\n'.format(_log_id, tsync_id))
            offset += 10000
            limit += 10000
            print(limit)
        csv.close()
