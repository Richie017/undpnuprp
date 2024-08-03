from datetime import datetime, timedelta

from django.core.management import BaseCommand
from django.db.models import Max, Count
from django.db.models import Min

from undp_nuprp.reports.config.constants.pg_survey_constants import *
from undp_nuprp.reports.models import PGMemberInfoCache
from undp_nuprp.survey.models import SurveyResponse, QuestionResponse

__author__ = 'Ziaul Haque'


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.generate_pg_member_indicator_cache()

    @classmethod
    def generate_pg_member_indicator_cache(cls):
        time_from = PGMemberInfoCache.objects.filter(
            pg_member_difficulty_counts=0, pg_member_no_difficulty_counts=0
        ).aggregate(Min('from_time'))['from_time__min']
        if time_from is None:
            first_pg_survey = SurveyResponse.objects.filter(
                survey__name__icontains=PG_MEMBER_SURVEY_NAME).aggregate(Min('date_created'))['date_created__min']
            if first_pg_survey:
                dt = datetime.fromtimestamp(first_pg_survey / 1000).replace(hour=0, minute=0, second=0)
            else:
                dt = datetime.now().replace(hour=0, minute=0, second=0)
        else:
            dt = datetime.fromtimestamp(time_from / 1000)
        cls.generate(time=dt)

    @classmethod
    def generate(cls, time=None):
        if time is None:
            time = datetime.now() - timedelta(days=1)
        to_date = datetime.now()

        cutoff_time = PGMemberInfoCache.objects.filter(
            pg_member_difficulty_counts=0, pg_member_no_difficulty_counts=0
        ).aggregate(Max('date_created'))['date_created__max']
        if cutoff_time is None:
            cutoff_time = 0
        cutoff_time += 1
        cls.generate_cache_in_period(time, to_date, cutoff_time)

    @classmethod
    def generate_cache_in_period(cls, from_date, to_date, cutoff_time, logging=False):
        while from_date.date() <= to_date.date():
            print("generating cache for %s" % (from_date.strftime('%d/%m/%Y')))
            cls.cache_intervaled_report(from_time=from_date.replace(hour=0, minute=0, second=0).timestamp() * 1000,
                                        to_time=min(from_date.replace(hour=23, minute=59, second=59).timestamp() * 1000,
                                                    cutoff_time),
                                        logging=logging)
            from_date += timedelta(days=1)

    @classmethod
    def cache_intervaled_report(cls, from_time, to_time, logging=False):
        date = datetime.fromtimestamp(from_time / 1000).date()

        in_hand_records = dict()

        # Handle PG member with difficulties count
        question_responses = QuestionResponse.objects.filter(
            section_response__survey_response__survey__name__icontains=PG_MEMBER_SURVEY_NAME,
            section_response__survey_response__date_created__gte=from_time,
            section_response__survey_response__date_created__lte=to_time,
            question__question_code__in=DISABLITY_QUESTION_CODE,
            answer_text__in=DISABLED_ANSWER_TEXT
        ).values(
            'question__question_code',
            'section_response__survey_response__respondent_client__assigned_to__parent__address__geography_id',
            'section_response__survey_response__respondent_client__assigned_to__parent__address__geography__parent_id'
        ).annotate(
            count=Count('section_response__survey_response__pk', distinct=True)
        )
        for q in question_responses:
            ward_id = q[
                'section_response__survey_response__respondent_client__assigned_to__parent__address__geography_id']
            city_id = q[
                'section_response__survey_response__respondent_client__assigned_to__parent__address__geography__parent_id']

            record = PGMemberInfoCache.get_record(
                date=date, from_time=from_time, to_time=to_time, ward_id=ward_id, city_id=city_id,
                in_hand_records=in_hand_records)

            record.pg_member_difficulty_counts = q['count']
            record.save()

        # Handle PG member with no difficulties count
        question_responses = QuestionResponse.objects.filter(
            section_response__survey_response__survey__name__icontains=PG_MEMBER_SURVEY_NAME,
            section_response__survey_response__date_created__gte=from_time,
            section_response__survey_response__date_created__lte=to_time,
            question__question_code__in=DISABLITY_QUESTION_CODE
        ).exclude(
            answer_text__in=DISABLED_ANSWER_TEXT
        ).values(
            'question__question_code',
            'section_response__survey_response__respondent_client__assigned_to__parent__address__geography_id',
            'section_response__survey_response__respondent_client__assigned_to__parent__address__geography__parent_id'
        ).annotate(
            count=Count('section_response__survey_response__pk', distinct=True)
        )
        for q in question_responses:
            ward_id = q[
                'section_response__survey_response__respondent_client__assigned_to__parent__address__geography_id']
            city_id = q[
                'section_response__survey_response__respondent_client__assigned_to__parent__address__geography__parent_id']

            record = PGMemberInfoCache.get_record(
                date=date, from_time=from_time, to_time=to_time, ward_id=ward_id, city_id=city_id,
                in_hand_records=in_hand_records)

            record.pg_member_no_difficulty_counts = q['count']
            record.save()
