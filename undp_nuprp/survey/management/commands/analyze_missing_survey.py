"""
Created by tareq on 4/9/18
"""

import json
from datetime import datetime

from django.core.management import BaseCommand

from blackwidow.core.models import *
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models import *
from undp_nuprp.survey.models import *

__author__ = 'Tareq'


class Command(BaseCommand):
    def handle(self, *args, **options):
        api_logs = ApiCallLog.objects.filter(request_type='POST', url__icontains='survey-response').exclude(
            response_data__icontains='201').order_by('date_created')

        missed = 0
        found = 0
        doomed = 0
        recoverable = 0
        user_match = 0
        user_mismatch = 0
        one_sided = 0

        doomed_dict = dict()
        recoverable_dict = dict()
        missed_dict = dict()

        _t = api_logs.count()
        _h = 1
        csv = open("missed_api_logs.csv", "w")
        csv.write(
            "API Log id,Time,City,Ward,PG,Enumerator,Last enumerator in PG,Next enumerator in PG,Time from last survey in PG,Time to next survey in PG\n")
        for api_log in api_logs:
            print('{}/{}'.format(_h, _t))
            _h += 1
            body = api_log.request_body
            if body:
                try:
                    body = json.loads(body)
                except:
                    continue

                tsync_id = body['tsync_id']
                if tsync_id in doomed_dict.keys():
                    continue
                survey_response = SurveyResponse.objects.filter(
                    tsync_id=tsync_id).first()
                if survey_response is None:
                    missed += 1
                    print("missed at " + str(datetime.fromtimestamp(api_log.date_created / 1000)))

                    if 'address' in body.keys():
                        pg_id = body['address']['poor_settlement']
                        ct = api_log.date_created
                    else:
                        continue
                    pg = ward = city = None
                    try:
                        pg = PrimaryGroup.objects.get(id=pg_id)
                        ward = pg.parent.address.geography.name
                        city = pg.parent.address.geography.parent.name
                    except:
                        pass

                    if city not in missed_dict.keys():
                        missed_dict[city] = 0
                    missed_dict[city] += 1

                    last_pgm = PrimaryGroupMember.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                        assigned_to_id=pg_id, date_created__lt=ct).order_by(
                        '-date_created').first()
                    next_pgm = PrimaryGroupMember.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                        assigned_to_id=pg_id,
                        date_created__gt=ct).order_by(
                        'date_created').first()

                    _log_id = api_log.pk
                    _time = str(datetime.fromtimestamp(api_log.date_created / 1000))
                    _city = city
                    _ward = ward
                    _pg = pg.name if pg else '-'
                    _enumerator = api_log.created_by.user.username if api_log.created_by else (
                        api_log.last_updated_by.user.username if api_log.last_updated_by else '-')
                    _prev = last_pgm.created_by.user.username if last_pgm else '-'
                    _next = next_pgm.created_by.user.username if next_pgm else '-'
                    _prev_time = str(int((api_log.date_created - last_pgm.date_created) / 1000)) if last_pgm else '-'
                    _next_time = str(int((next_pgm.date_created - api_log.date_created) / 1000)) if next_pgm else '-'
                    _match = 'Yes' if _prev == _next and last_pgm and next_pgm else 'No'

                    csv.write(
                        '{},{},{},{},{},{},{},{},{},{},{}\n'.format(_log_id, _time, _city, _ward, _pg, _enumerator,
                                                                    _prev, _next, _match, _prev_time, _next_time))
                    if last_pgm is None and next_pgm is None:
                        doomed += 1
                        if city not in doomed_dict.keys():
                            doomed_dict[city] = 0
                        doomed_dict[city] += 1
                    else:
                        user_1 = last_pgm.created_by.user.username if last_pgm else ''
                        user_2 = next_pgm.created_by.user.username if next_pgm else ''
                        if user_1 != user_2 and user_1 and user_2:
                            user_mismatch += 1
                        elif user_1 == user_2:
                            user_match += 1
                        else:
                            one_sided += 1
                        user = user_1 if user_1 else user_2
                        if city not in recoverable_dict.keys():
                            recoverable_dict[city] = dict()
                        if user not in recoverable_dict[city].keys():
                            recoverable_dict[city][user] = 0
                        recoverable_dict[city][user] += 1
                        recoverable += 1


                else:
                    found += 1

        print("User mismatch " + str(user_mismatch))
        print("User match " + str(user_match))
        print("User one-sided " + str(one_sided))
        print("Found " + str(found))
        print("Missed " + str(missed))
        for k, v in missed_dict.items():
            print(k, v)
        print("doomed: " + str(doomed))
        for k, v in doomed_dict.items():
            print(k, v)
        print("Recoverable: " + str(recoverable))
        for city, d in recoverable_dict.items():
            print(city)
            total = 0
            for u, v in d.items():
                print(u, v)
                total += v
            print("Total>>> " + str(total))

        csv.close()
