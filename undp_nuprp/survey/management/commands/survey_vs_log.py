"""
Created by tareq on 4/9/18
"""

import json
from datetime import datetime

from django.core.management import BaseCommand

from blackwidow.core.models import *
from undp_nuprp.nuprp_admin.models import *
from undp_nuprp.survey.models import *

__author__ = 'Tareq'


class Command(BaseCommand):
    def handle(self, *args, **options):
        from datetime import datetime

        d_start = datetime(year=2018, month=3, day=30).timestamp() * 1000
        d_end = datetime(year=2018, month=4, day=11).timestamp() * 1000

        csv = open('survey_vs_log.csv', 'w')
        csv.write("Survey id,API id,201 found?,is missed?\n")

        for survey in SurveyResponse.objects.using('replica').filter(date_created__gt=d_start, date_created__lt=d_end):
            print("checking for survey: " + str(survey.tsync_id))
            tsync_id = survey.tsync_id

            _id = survey.id

            completed_queryset = ApiCallLog.objects.using('replica').filter(request_body__icontains=tsync_id,
                                                                            response_data__icontains='201')
            found_queryset = ApiCallLog.objects.using('replica').filter(request_body__icontains=tsync_id)

            if completed_queryset.exists():
                _201 = True
                _api = completed_queryset.first().pk
                _missed = False
            else:
                _201 = False
                _api = found_queryset.first()
                if _api:
                    _api = _api.pk
                    _missed = False
                else:
                    _api = None
                    _missed = True
            csv.write("{},{},{},{}\n".format(str(_id), str(_api), str(_201), str(_missed)))

        csv.close()
