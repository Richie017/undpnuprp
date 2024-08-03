"""
    Created by tareq on 3/13/17
"""

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from undp_nuprp.survey.models.export.survey_response_generated_file import SurveyResponseGeneratedFile

__author__ = 'Tareq'


class Command(BaseCommand):
    help = "parameter in format March,2017"

    def add_arguments(self, parser):
        parser.add_argument('date', nargs='+', type=str)

    def handle(self, *args, **options):
        given_date = datetime.strptime(options['date'][0], "%B,%Y")
        year = given_date.year
        month = given_date.month + 1
        if month > 12:
            month = 1
            year += 1
        given_date = given_date.replace(year=year, month=month)
        given_date -= timedelta(seconds=1)

        SurveyResponseGeneratedFile.generate_export_files_in_given_time(generation_time=given_date)
