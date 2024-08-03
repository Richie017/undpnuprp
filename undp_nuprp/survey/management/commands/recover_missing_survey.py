"""
Created by tareq on 4/9/18
"""

import json
import time

import requests
from django.core.management import BaseCommand
from rest_framework.authtoken.models import Token

from blackwidow.core.models import *
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models import *
from undp_nuprp.survey.models import *

__author__ = 'Tareq'


class Command(BaseCommand):
    def handle(self, *args, **options):
        site = 'https://api.nuprp.info/'
        api_url = site + 'api/survey-response/'

        total_recovered = 0
        for enumerator in Enumerator.objects.all():
            print('Handling: {}'.format(enumerator, ))
            api_logs = ApiCallLog.objects.filter(request_type='POST', url__icontains='survey-response',
                                                 created_by_id=enumerator.pk).exclude(
                response_data__icontains='201').order_by('date_created')

            missed = 0
            found = 0
            doomed = 0

            post_list = list()

            total_candidate = api_logs.count()
            looked_up = 0
            t_dict = dict()
            used_dict = dict()
            for api_log in api_logs:
                body = api_log.request_body
                looked_up += 1
                print("Looked up {}/{}".format(looked_up, total_candidate))
                if body:
                    try:
                        body = json.loads(body)
                    except:
                        continue
                    tsync_id = body['tsync_id']
                    if tsync_id in used_dict.keys():
                        continue
                    used_dict[tsync_id] = True
                    survey_response = SurveyResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                        tsync_id=tsync_id).first()
                    if survey_response is None:
                        missed += 1

                        if 'address' not in body.keys():
                            continue

                        pg_id = body['address']['poor_settlement']
                        ct = api_log.date_created

                        last_pgm = PrimaryGroupMember.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                            assigned_to_id=pg_id, date_created__lt=ct).order_by(
                            '-date_created').first()
                        next_pgm = PrimaryGroupMember.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                            assigned_to_id=pg_id,
                            date_created__gt=ct).order_by(
                            'date_created').first()

                        user = api_log.created_by if api_log.created_by else api_log.last_updated_by
                        if user and user.type != Enumerator.__name__:
                            user = None
                        if last_pgm is None and next_pgm is None and not user:
                            doomed += 1
                            pg = PrimaryGroup.objects.get(pk=pg_id)
                            city = pg.parent.address.geography.parent.name
                            if city not in t_dict.keys():
                                t_dict[city] = 0
                            t_dict[city] += 1
                        else:
                            user_1 = last_pgm.created_by if last_pgm else None
                            user_2 = next_pgm.created_by if next_pgm else None
                            if not user:
                                if user_1 and user_2 and user_1 == user_2:
                                    user = user_1
                            if not user and user_1:
                                user = user_1
                            if not user and user_2:
                                user = user_2
                            token = Token.objects.using(BWDatabaseRouter.get_read_database_name()).using(
                                BWDatabaseRouter.get_read_database_name()).filter(
                                user_id=user.user_id).order_by('-created').first()
                            if token is not None and token.key:
                                key = token.key
                                headers = {
                                    'Content-Type': 'application/json',
                                    'Authorization': 'Token ' + str(key)
                                }
                                post_list.append({
                                    'data': body,
                                    'headers': headers,
                                    'user': user.name,
                                    'api_log': api_log.id
                                })

                            if user_2 is None or user_1 is None:
                                pass

                    else:
                        found += 1

            print("Found " + str(found))
            print("Missed " + str(missed))
            print("doomed:")
            for k, v in t_dict.items():
                print(k, v)

            total_postable = len(post_list)
            print("Recoverable: " + str(total_postable))
            posted = 0
            for p in post_list:
                t1 = time.time()
                print("Attempting post for user {} ({})...".format(p['user'], p['api_log']))
                response = requests.post(api_url, data=json.dumps(p['data']), headers=p['headers'])
                t2 = time.time()
                posted += 1
                total_recovered += 1
                print("%d/%d posted, response found in %ld" % (posted, total_postable, t2 - t1))
                print(response)

        print("Total recovered: {}".format(total_recovered, ))
