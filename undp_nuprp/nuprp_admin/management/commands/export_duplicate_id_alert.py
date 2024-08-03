"""
    Created by tareq on ১২/৭/২০
"""

__author__ = "Tareq"

from django.core.management import BaseCommand
from django.apps import apps
from django.urls import reverse

from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from config.database import READ_DATABASE_NAME
from undp_nuprp.nuprp_admin.models import DuplcateIdAlert
from undp_nuprp.survey.models import SurveyResponse


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("duplicate_id_alert.csv", "w") as file:
            file.write("Code,City,Alert Type,PG Member,Survey Response,Reason,Enumerator,Alert Generation Time\n")
            offset = 0
            limit = 100

            total = DuplcateIdAlert.objects.count()
            while True:
                print("Processing: {} - {} of {}".format(offset, offset + limit, total))
                alerts = list(DuplcateIdAlert.objects.using(READ_DATABASE_NAME).all()[offset:offset + limit])

                for alert in alerts:
                    code = alert.code

                    city = "N/A"
                    try:
                        if alert.created_by:
                            _address = alert.created_by.addresses.first()
                            if _address and _address.geography:
                                city = _address.geography.parent.name if _address.geography.parent else "N/A"
                    except:
                        pass

                    alert_type = alert.model_property

                    try:
                        client = apps.get_model(alert.app_label, alert.model).all_objects.get(pk=alert.object_id)
                        member = "{} (https://nuprpbd.info{})".format(
                            client.name,
                            reverse(client.get_route_name(ViewActionEnum.Details), kwargs={"pk": client.pk}))
                    except:
                        member = 'Not Found'

                    survey_response = "N/A"
                    try:
                        sr = SurveyResponse.objects.filter(respondent_client__id=alert.object_id).first()
                        if sr:
                            survey_response = "https://nuprpbd.info{}".format(
                                reverse(sr.get_route_name(ViewActionEnum.Details), kwargs={"pk": sr.pk}))
                    except:
                        pass

                    enumerator = "N/A"
                    try:
                        en = alert.created_by
                        if en:
                            enumerator = "{} (https://nuprpbd.info{})".format(
                                en.name, reverse(en.get_route_name(ViewActionEnum.Details), kwargs={"pk": sr.pk}))
                    except:
                        pass

                    time = alert.alert_creation_time
                    detail = str(alert.alert_detail)

                    try:
                        detail_parts = detail.split("of,")
                        prefix = detail_parts[0] + "of"
                        member_id = detail_parts[1].split("details/")[1].replace("'", '"').split('"')[0]
                        member_name = detail_parts[1].split(">")[1].split("<")[0]
                        detail = "{} {} (https://nuprpbd.info/en/primary-group-members/details/{})".format(
                            prefix, member_name, member_id
                        )
                    except:
                        pass

                    file.write('"{}","{}","{}","{}","{}","{}","{}","{}"\n'.format(
                        code, city, alert_type, member, survey_response, detail, enumerator, time
                    ))

                if len(alerts) < limit:
                    break
                offset += limit
