import datetime

from datetime import timedelta
from django.core.management.base import BaseCommand

from undp_nuprp.survey.managers.pg_survey_deletion_manager import PGSurveyDeletionManager

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        from_date = input('From Date: ')
        to_date = input('To Date: ')
        city = input('City: ')

        _date_format = '%d/%m/%Y'

        from_date = datetime.datetime.strptime(from_date, _date_format)
        from_date = from_date.replace(year=from_date.year, month=from_date.month, day=from_date.day, hour=0,
                                      minute=0, second=0, microsecond=0)
        from_date = int(from_date.timestamp() * 1000)

        to_date = datetime.datetime.strptime(to_date, _date_format)
        to_date = to_date + timedelta(1)

        to_date = to_date.replace(year=to_date.year, month=to_date.month, day=to_date.day, hour=0,
                                  minute=0, second=0, microsecond=0)

        to_date = int(to_date.timestamp() * 1000) - 1

        print('Starting deletion operation')

        PGSurveyDeletionManager.delete_pg_survey_and_its_reference(from_time=from_date, to_time=to_date, city=city)

        print('Deletion operation completed')
