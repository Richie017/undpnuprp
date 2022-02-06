"""
Created by tareq on 3/20/18
"""
import sys
from datetime import datetime

from django.db.models import Max, Min, Func, F, DateTimeField, Value, CharField
from django.db.models.functions import Cast

from undp_nuprp.reports.config.constants.pg_survey_constants import PG_MEMBER_SURVEY_NAME
from undp_nuprp.reports.models import PGMemberInfoCache
from undp_nuprp.survey.models import SurveyResponse

__author__ = 'Tareq'


class PGMemberIndicatorManager(object):
    @classmethod
    def generate_pg_member_indicator_cache(cls, from_timestamp=None, to_time=None):
        time_from = from_timestamp or PGMemberInfoCache.objects.aggregate(Max('from_time'))['from_time__max']
        if time_from is None:
            first_pg_survey = SurveyResponse.objects.filter(
                survey__name__icontains=PG_MEMBER_SURVEY_NAME).aggregate(Min('date_created'))['date_created__min']
            if first_pg_survey:
                dt = datetime.fromtimestamp(first_pg_survey / 1000).replace(hour=0, minute=0, second=0)
            else:
                dt = datetime.now().replace(hour=0, minute=0, second=0)
        else:
            dt = datetime.fromtimestamp(time_from / 1000)
        PGMemberInfoCache.generate(time=dt)
        if not to_time:
            to_time = datetime.now().timestamp() * 1000

        # Now handle updated survey-responses which were created long ago
        updated_queryset = SurveyResponse.all_objects.filter(
            last_updated__gt=time_from, date_created__lt=to_time).annotate(**{
            'year': Cast(Func(
                Cast(Func(
                    F('date_created') / 1000,
                    # convert millisecond timestamp to Python+PG supported second timestamp
                    function='to_timestamp'),  # convert timestamp into PG timestamp (datetime) object
                    DateTimeField()),  # assign converted field into a date-time-field
                Value('YYYY'),  # Pass the format of date field
                function='to_char'  # convert the date-time object to a date String
            ), CharField(max_length=32))
        }).annotate(**{
            'month': Cast(Func(
                Cast(Func(
                    F('date_created') / 1000,
                    # convert millisecond timestamp to Python+PG supported second timestamp
                    function='to_timestamp'),  # convert timestamp into PG timestamp (datetime) object
                    DateTimeField()),  # assign converted field into a date-time-field
                Value('MM'),  # Pass the format of date field
                function='to_char'  # convert the date-time object to a date String
            ), CharField(max_length=32))
        }).annotate(**{
            'day': Cast(Func(
                Cast(Func(
                    F('date_created') / 1000,
                    # convert millisecond timestamp to Python+PG supported second timestamp
                    function='to_timestamp'),  # convert timestamp into PG timestamp (datetime) object
                    DateTimeField()),  # assign converted field into a date-time-field
                Value('DD'),  # Pass the format of date field
                function='to_char'  # convert the date-time object to a date String
            ), CharField(max_length=32))
        })

        updated_queryset = updated_queryset.distinct('year', 'month', 'day').order_by('year', 'month', 'day').values(
            'year', 'month', 'day')

        for d in updated_queryset:
            print(d)
            
        for individual_date in updated_queryset:
            report_datetime = datetime(
                year=int(individual_date['year']), month=int(individual_date['month']), day=int(individual_date['day']))

            report_date = report_datetime
            print("Regenerating cache for {}.".format(report_date))
            PGMemberInfoCache.generate_cache_in_period(from_date=report_date, to_date=report_date,
                                                       cutoff_time=sys.maxsize)
