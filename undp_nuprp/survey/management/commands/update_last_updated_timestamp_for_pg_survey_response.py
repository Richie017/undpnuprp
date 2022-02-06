import csv
import os

from django.core.management import BaseCommand

from blackwidow.engine.extensions import Clock
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from settings import STATIC_ROOT
from undp_nuprp.survey.models import SurveyResponse

__author__ = "Ziaul Haque"


class Command(BaseCommand):
    def load_data_from_csv(self, csv_path):
        with open(csv_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            data = []
            for row in csv_reader:
                data.append(row)
            return data

    def handle(self, *args, **options):
        survey_id = 3

        filename = os.path.join(STATIC_ROOT, 'data/pg_survey_responses.csv')
        processable_survey_responses = self.load_data_from_csv(filename)[1:]
        response_ids = []
        for item in processable_survey_responses:
            response_ids.append(item[0])

        queryset = SurveyResponse.objects.filter(
            survey_id=survey_id, pk__in=response_ids
        ).using(BWDatabaseRouter.get_write_database_name())

        current_timestamp = Clock.timestamp()
        updatable_entries = []
        counter = 0
        for r in queryset:
            r.last_updated = current_timestamp
            updatable_entries.append(r)
            current_timestamp += 1
            counter += 1

            if len(updatable_entries) % 1000 == 0:
                SurveyResponse.objects.bulk_update(updatable_entries, batch_size=1000)
                print("{0} entries updated...".format(counter))
                updatable_entries = []

        SurveyResponse.objects.bulk_update(updatable_entries, batch_size=1000)
        print("{0} entries updated...".format(counter))
