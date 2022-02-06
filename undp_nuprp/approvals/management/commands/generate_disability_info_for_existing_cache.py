from datetime import datetime, timedelta

from django.core.management import BaseCommand
from django.db.models import Max
from django.db.models import Min

from undp_nuprp.reports.config.constants.pg_survey_constants import *
from undp_nuprp.reports.models import PGMemberInfoCache
from undp_nuprp.survey.models import SurveyResponse

__author__ = 'Ziaul Haque'


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.generate_pg_member_indicator_cache()
        
    @classmethod
    def generate_pg_member_indicator_cache(cls):
        time_from = PGMemberInfoCache.objects.filter(
            difficulty_in_seeing_counts__isnull=True,
            difficulty_in_hearing_counts__isnull=True,
            difficulty_in_walking_counts__isnull=True,
            difficulty_in_remembering_counts__isnull=True,
            difficulty_in_self_care_counts__isnull=True,
            difficulty_in_communicating_counts__isnull=True,

            hh_difficulty_in_seeing_counts__isnull=True,
            hh_difficulty_in_hearing_counts__isnull=True,
            hh_difficulty_in_walking_counts__isnull=True,
            hh_difficulty_in_remembering_counts__isnull=True,
            hh_difficulty_in_self_care_counts__isnull=True,
            hh_difficulty_in_communicating_counts__isnull=True,
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
            difficulty_in_seeing_counts__isnull=True,
            difficulty_in_hearing_counts__isnull=True,
            difficulty_in_walking_counts__isnull=True,
            difficulty_in_remembering_counts__isnull=True,
            difficulty_in_self_care_counts__isnull=True,
            difficulty_in_communicating_counts__isnull=True,

            hh_difficulty_in_seeing_counts__isnull=True,
            hh_difficulty_in_hearing_counts__isnull=True,
            hh_difficulty_in_walking_counts__isnull=True,
            hh_difficulty_in_remembering_counts__isnull=True,
            hh_difficulty_in_self_care_counts__isnull=True,
            hh_difficulty_in_communicating_counts__isnull=True,
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

        # Handle Difficulty in Seeing counts
        PGMemberInfoCache.prepare_key_value_count_for_single_question(
            DIFFICULTY_IN_SEEING_QUESTION_CODE, PGMemberInfoCache.difficulty_in_seeing_counts,
            from_time, to_time, date, in_hand_records)

        # Handle Difficulty in Hearing counts
        PGMemberInfoCache.prepare_key_value_count_for_single_question(
            DIFFICULTY_IN_HEARING_QUESTION_CODE, PGMemberInfoCache.difficulty_in_hearing_counts,
            from_time, to_time, date, in_hand_records)

        # Handle Difficulty in Walking counts
        PGMemberInfoCache.prepare_key_value_count_for_single_question(
            DIFFICULTY_IN_WALKING_QUESTION_CODE, PGMemberInfoCache.difficulty_in_walking_counts,
            from_time, to_time, date, in_hand_records)

        # Handle Difficulty in Remembering counts
        PGMemberInfoCache.prepare_key_value_count_for_single_question(
            DIFFICULTY_IN_REMEMBERING_QUESTION_CODE, PGMemberInfoCache.difficulty_in_remembering_counts,
            from_time, to_time, date, in_hand_records)

        # Handle Difficulty in Self Care counts
        PGMemberInfoCache.prepare_key_value_count_for_single_question(
            DIFFICULTY_IN_SELF_CARE_QUESTION_CODE, PGMemberInfoCache.difficulty_in_self_care_counts,
            from_time, to_time, date, in_hand_records)

        # Handle Difficulty in Communicating counts
        PGMemberInfoCache.prepare_key_value_count_for_single_question(
            DIFFICULTY_IN_COMMUNICATING_QUESTION_CODE, PGMemberInfoCache.difficulty_in_communicating_counts,
            from_time, to_time, date, in_hand_records)

        # Handle HH Difficulty in Seeing counts
        PGMemberInfoCache.prepare_key_value_count_for_single_question(
            HH_DIFFICULTY_IN_SEEING_QUESTION_CODE, PGMemberInfoCache.hh_difficulty_in_seeing_counts,
            from_time, to_time, date, in_hand_records)

        # Handle HH Difficulty in Hearing counts
        PGMemberInfoCache.prepare_key_value_count_for_single_question(
            HH_DIFFICULTY_IN_HEARING_QUESTION_CODE, PGMemberInfoCache.hh_difficulty_in_hearing_counts,
            from_time, to_time, date, in_hand_records)

        # Handle HH Difficulty in Walking counts
        PGMemberInfoCache.prepare_key_value_count_for_single_question(
            HH_DIFFICULTY_IN_WALKING_QUESTION_CODE, PGMemberInfoCache.hh_difficulty_in_walking_counts,
            from_time, to_time, date, in_hand_records)

        # Handle HH Difficulty in Remembering counts
        PGMemberInfoCache.prepare_key_value_count_for_single_question(
            HH_DIFFICULTY_IN_REMEMBERING_QUESTION_CODE, PGMemberInfoCache.hh_difficulty_in_remembering_counts,
            from_time, to_time, date, in_hand_records)

        # Handle HH Difficulty in Self Care counts
        PGMemberInfoCache.prepare_key_value_count_for_single_question(
            HH_DIFFICULTY_IN_SELF_CARE_QUESTION_CODE, PGMemberInfoCache.hh_difficulty_in_self_care_counts,
            from_time, to_time, date, in_hand_records)

        # Handle HH Difficulty in Communicating counts
        PGMemberInfoCache.prepare_key_value_count_for_single_question(
            HH_DIFFICULTY_IN_COMMUNICATING_QUESTION_CODE, PGMemberInfoCache.hh_difficulty_in_communicating_counts,
            from_time, to_time, date, in_hand_records)