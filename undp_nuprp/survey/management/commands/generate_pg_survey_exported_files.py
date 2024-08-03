from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from undp_nuprp.survey.models.export.survey_response_generated_file import SurveyResponseGeneratedFile

__author__ = 'Ziaul Haque'


class Command(BaseCommand):
    help = "parameter in format March,2017"

    def add_arguments(self, parser):
        parser.add_argument('date', nargs='+', type=str)

    def handle(self, *args, **options):
        for date in options['date']:
            print("populating export file for month: {0}".format(date))
            given_date = datetime.strptime(date, "%B,%Y")
            year = given_date.year
            month = given_date.month + 1
            if month > 12:
                month = 1
                year += 1
            given_date = given_date.replace(year=year, month=month)
            given_date -= timedelta(seconds=1)

            survey_id = 3
            month_start = given_date.replace(day=1, hour=0, minute=0, second=0).timestamp() * 1000
            year = int(given_date.strftime("%Y"))  # Clock.millisecond_to_date_str(time_to, _format="%Y")
            month = int(given_date.strftime("%m"))  # Clock.millisecond_to_date_str(time_to, _format="%B")

            existing_file = SurveyResponseGeneratedFile.objects.filter(
                year=year, survey_id=survey_id, month=month, format='Excel'
            ).order_by('-date_created').first()
            if existing_file:
                SurveyResponseGeneratedFile.objects.filter(pk=existing_file.pk).update(last_updated=month_start)

            SurveyResponseGeneratedFile.generate_export_files_in_given_time(
                generation_time=given_date,
                survey_id=survey_id,
                mode='w'
            )
            print("export file generated...")
