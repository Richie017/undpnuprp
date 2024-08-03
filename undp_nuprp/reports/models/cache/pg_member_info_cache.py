"""
Created by tareq on 2/12/18
"""
from datetime import datetime, timedelta

from django.db import models
from django.db.models import Count, IntegerField, Sum, Max
from django.db.models.functions import Cast

from blackwidow.core.models.contracts.base import DomainEntity
from undp_nuprp.reports.config.constants.pg_survey_constants import *
from undp_nuprp.reports.models.cache.key_value_count import KeyValueCount
from undp_nuprp.survey.models.indicators.pg_mpi_indicator.mpi_indicator import PGMPIIndicator
from undp_nuprp.survey.models.response.question_response import QuestionResponse

__author__ = 'Tareq'


class PGMemberInfoCache(DomainEntity):
    year = models.IntegerField(default=1970)
    month = models.IntegerField(default=1)
    day = models.IntegerField(default=1)
    from_time = models.BigIntegerField(default=0)
    to_time = models.BigIntegerField(default=24 * 3600 * 1000)

    city = models.ForeignKey('core.Geography', null=True, on_delete=models.SET_NULL, related_name='+')
    ward = models.ForeignKey('core.Geography', null=True, on_delete=models.SET_NULL, related_name='+')
    pg_count = models.IntegerField(default=0)

    household_head_count = models.IntegerField(default=0)
    household_member_count = models.IntegerField(default=0)
    household_male_member_count = models.IntegerField(default=0)
    household_female_member_count = models.IntegerField(default=0)
    household_pregnancy_count = models.IntegerField(default=0)
    household_lactating_mother_count = models.IntegerField(default=0)
    household_with_lactating_mother_count = models.IntegerField(default=0)
    household_without_lactating_mother_count = models.IntegerField(default=0)
    household_children_count = models.IntegerField(default=0)
    household_with_children_count = models.IntegerField(default=0)
    household_without_children_count = models.IntegerField(default=0)
    household_adolescent_girl_count = models.IntegerField(default=0)
    household_with_adolescent_girl_count = models.IntegerField(default=0)
    household_without_adolescent_girl_count = models.IntegerField(default=0)
    household_disability_count = models.IntegerField(default=0)
    household_with_disability_count = models.IntegerField(default=0)
    household_without_disability_count = models.IntegerField(default=0)

    gender_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    religion_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    ethnicity_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    marital_status_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    education_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    employment_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    age_group_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    disability_counts = models.ManyToManyField(KeyValueCount, related_name='+')

    hh_gender_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    hh_employment_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    hh_education_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    hh_disability_counts = models.ManyToManyField(KeyValueCount, related_name='+')

    pg_member_difficulty_counts = models.IntegerField(default=0)
    pg_member_no_difficulty_counts = models.IntegerField(default=0)

    difficulty_in_seeing_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    difficulty_in_hearing_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    difficulty_in_walking_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    difficulty_in_remembering_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    difficulty_in_self_care_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    difficulty_in_communicating_counts = models.ManyToManyField(KeyValueCount, related_name='+')

    hh_difficulty_in_seeing_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    hh_difficulty_in_hearing_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    hh_difficulty_in_walking_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    hh_difficulty_in_remembering_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    hh_difficulty_in_self_care_counts = models.ManyToManyField(KeyValueCount, related_name='+')
    hh_difficulty_in_communicating_counts = models.ManyToManyField(KeyValueCount, related_name='+')

    class Meta:
        app_label = 'reports'
        index_together = [
            ['year', 'month', 'day']
        ]

    @classmethod
    def generate(cls, time=None):
        if time is None:
            time = datetime.now() - timedelta(days=1)
        to_date = datetime.now()

        cutoff_time = PGMPIIndicator.objects.aggregate(Max('survey_response__date_created'))[
            'survey_response__date_created__max']
        if cutoff_time is None:
            cutoff_time = 0
        cutoff_time += 1
        cls.generate_cache_in_period(time, to_date, cutoff_time)

    @classmethod
    def generate_cache_in_period(cls, from_date, to_date, cutoff_time, logging=False):
        while from_date.date() <= to_date.date():
            print("clearing cache for %s".format(from_date))
            cls.objects.filter(year=from_date.year, month=from_date.month, day=from_date.day).delete()
            print("...Cleared")
            print("generating cache between %s to %s" % (from_date.strftime('%d/%m/%Y'), to_date.strftime('%d/%m/%Y')))
            cls.cache_intervaled_report(from_time=from_date.replace(hour=0, minute=0, second=0).timestamp() * 1000,
                                        to_time=min(from_date.replace(hour=23, minute=59, second=59).timestamp() * 1000,
                                                    cutoff_time),
                                        logging=logging)
            from_date += timedelta(days=1)

    @classmethod
    def get_record(cls, date, from_time, to_time, ward_id, city_id, in_hand_records):
        # First, check if we already had this record previously
        if (date.year, date.month, date.day, ward_id) in in_hand_records.keys():
            record = in_hand_records[(date.year, date.month, date.day, ward_id)]
        else:
            # We did not work with this record yet. Check if it exists in the database
            record = cls.objects.filter(
                year=date.year, month=date.month, day=date.day, ward_id=ward_id).first()
            if record is None:
                # The record is not in the database, so let's create it
                record = cls(year=date.year, month=date.month, day=date.day, ward_id=ward_id, city_id=city_id,
                             from_time=from_time, to_time=to_time)
                record.save()
            # Save it in_hand_records, so that we can use it later
            in_hand_records[(date.year, date.month, date.day, ward_id)] = record
        return record

    @classmethod
    def cache_intervaled_report(cls, from_time, to_time, logging=False):
        date = datetime.fromtimestamp(from_time / 1000).date()
        print("Caching indicators for " + str(date))
        in_hand_records = dict()

        # Total PG member count
        question_responses = QuestionResponse.objects.filter(
            section_response__survey_response__survey__name__icontains=PG_MEMBER_SURVEY_NAME,
            section_response__survey_response__date_created__gte=from_time,
            section_response__survey_response__date_created__lte=to_time
        ).values(
            'section_response__survey_response__respondent_client__assigned_to__parent__address__geography_id',
            # Ward id
            'section_response__survey_response__respondent_client__assigned_to__parent__address__geography__parent_id'
            # city id
        ).annotate(
            count=Count('section_response__survey_response__pk', distinct=True)
        )
        for q in question_responses:
            ward_id = q[
                'section_response__survey_response__respondent_client__assigned_to__parent__address__geography_id']
            city_id = q[
                'section_response__survey_response__respondent_client__assigned_to__parent__address__geography__parent_id']

            record = cls.get_record(
                date=date, from_time=from_time, to_time=to_time, ward_id=ward_id, city_id=city_id,
                in_hand_records=in_hand_records)

            record.pg_count = q['count']
            record.save()

        # Age Group Count
        print("Age indicator for " + str(date))
        question_responses = QuestionResponse.objects.filter(
            section_response__survey_response__survey__name__icontains=PG_MEMBER_SURVEY_NAME,
            section_response__survey_response__date_created__gte=from_time,
            section_response__survey_response__date_created__lte=to_time,
            question__question_code=AGE_QUESTION_CODE
        ).values(
            'section_response__survey_response__respondent_client__client_meta__age',
            'section_response__survey_response__respondent_client__assigned_to__parent__address__geography_id',
            'section_response__survey_response__respondent_client__assigned_to__parent__address__geography__parent_id'
        ).annotate(
            count=Count('pk', distinct=True)
        )

        # Clear all age-group counts first
        age_groups = dict()
        for q in question_responses:
            age = q['section_response__survey_response__respondent_client__client_meta__age']
            if not age:
                continue
            ward_id = q[
                'section_response__survey_response__respondent_client__assigned_to__parent__address__geography_id']
            city_id = q[
                'section_response__survey_response__respondent_client__assigned_to__parent__address__geography__parent_id']

            record = cls.get_record(
                date=date, from_time=from_time, to_time=to_time, ward_id=ward_id, city_id=city_id,
                in_hand_records=in_hand_records)

            # Check if this key-value pair already exists or not
            try:
                if age < PG_MEMBER_AGE_LOWER_LIMIT:
                    age_group_index = -1
                elif age > PG_MEMBER_AGE_UPPER_LIMIT:
                    age_group_index = 101
                else:
                    # 1 is subtracted to maintain grouping by division of 5
                    age_group_index = (int(age) - PG_MEMBER_AGE_LOWER_LIMIT) // PG_MEMBER_AGE_GROUP_STEP
                if record not in age_groups.keys():
                    age_groups[record] = dict()
                if age_group_index not in age_groups[record].keys():
                    age_groups[record][age_group_index] = 0
                age_groups[record][age_group_index] += q['count']
            except:
                pass

        for record, record_dict in age_groups.items():
            for age_group_index, count in record_dict.items():
                key_value_count = record.age_group_counts.filter(label=str(age_group_index)).first()
                # Update (or create) the count
                if key_value_count is None:
                    key_value_count = KeyValueCount(label=str(age_group_index), count=count)
                else:
                    key_value_count.count = count
                key_value_count.save()
                record.age_group_counts.add(key_value_count)

        # Total HH count
        print("HH indicator for " + str(date))
        cls.prepare_yes_answer_frequency_count(
            cls.household_head_count,
            HH_QUESTION_CODE,
            from_time, to_time, date, in_hand_records
        )

        # Total Household Member count
        cls.prepare_hm_key_value_for_single_question(
            cls.household_member_count,
            HM_COUNT_QUESTION_CODE,
            from_time, to_time, date, in_hand_records
        )

        # Total Household Male Member count
        cls.prepare_hm_key_value_for_single_question(
            cls.household_male_member_count,
            HM_COUNT_MALE_QUESTION_CODE,
            from_time, to_time, date, in_hand_records
        )

        # Total Household Female Member count
        cls.prepare_hm_key_value_for_single_question(
            cls.household_female_member_count,
            HM_COUNT_FEMALE_QUESTION_CODE,
            from_time, to_time, date, in_hand_records
        )

        # Total Household Pregnant Member count
        cls.prepare_hm_key_value_for_single_question(
            cls.household_pregnancy_count,
            HM_PREGNANCY_COUNT_QUESTION_CODE,
            from_time, to_time, date, in_hand_records
        )

        # Total Household Lactating Mother count
        cls.prepare_hm_key_value_for_single_question(
            cls.household_lactating_mother_count,
            HM_LACTATING_MOTHER_COUNT_QUESTION_CODE,
            from_time, to_time, date, in_hand_records
        )

        # Total Household Children(5 year or younger) count
        cls.prepare_hm_key_value_for_single_question(
            cls.household_children_count,
            HM_CHILDREN_COUNT_QUESTION_CODE,
            from_time, to_time, date, in_hand_records
        )

        # Total Household Girls(10 to 18 years old) count
        cls.prepare_hm_key_value_for_single_question(
            cls.household_adolescent_girl_count,
            HM_GIRLS_10_to_18_COUNT_QUESTION_CODE,
            from_time, to_time, date, in_hand_records
        )

        # Total Household Member's disability count
        cls.prepare_hm_key_value_for_single_question(
            cls.household_disability_count,
            DISABILITY_COUNT_QUESTION_CODE,
            from_time, to_time, date, in_hand_records
        )

        # Total Household with lactating mother
        cls.prepare_yes_answer_frequency_count(
            cls.household_with_lactating_mother_count,
            HM_LACTATING_MOTHER_QUESTION_CODE,
            from_time, to_time, date, in_hand_records
        )

        # Total Household without lactating mother
        cls.prepare_no_answer_frequency_count(
            cls.household_without_lactating_mother_count,
            HM_LACTATING_MOTHER_QUESTION_CODE,
            from_time, to_time, date, in_hand_records
        )

        # Total Household count with children(5 or below 5 years old)
        cls.prepare_yes_answer_frequency_count(
            cls.household_with_children_count,
            HM_CHILDREN_QUESTION_CODE,
            from_time, to_time, date, in_hand_records
        )

        # Total Household without children(5 or below 5 years old)
        cls.prepare_no_answer_frequency_count(
            cls.household_without_children_count,
            HM_CHILDREN_QUESTION_CODE,
            from_time, to_time, date, in_hand_records
        )

        # Total Household with Adolescent girls
        cls.prepare_yes_answer_frequency_count(
            cls.household_with_adolescent_girl_count,
            HM_ADOLESCENT_GIRL_QUESTION_CODE,
            from_time, to_time, date, in_hand_records
        )

        # Total Household without Adolescent girls
        cls.prepare_no_answer_frequency_count(
            cls.household_without_adolescent_girl_count,
            HM_ADOLESCENT_GIRL_QUESTION_CODE,
            from_time, to_time, date, in_hand_records
        )

        # Total Household with disability
        cls.prepare_yes_answer_frequency_count(
            cls.household_with_disability_count,
            ANY_DISABLED_MEMBER_QUESTION_CODE,
            from_time, to_time, date, in_hand_records
        )

        # Total Household without disability
        cls.prepare_no_answer_frequency_count(
            cls.household_without_disability_count,
            ANY_DISABLED_MEMBER_QUESTION_CODE,
            from_time, to_time, date, in_hand_records
        )

        # Handle Gender counts
        print("Members indicator for " + str(date))
        cls.prepare_key_value_count_for_single_question(GENDER_QUESTION_CODE, cls.gender_counts, from_time, to_time,
                                                        date, in_hand_records)

        # Handle Religion counts
        cls.prepare_key_value_count_for_single_question(RELIGION_QUESTION_CODE, cls.religion_counts, from_time, to_time,
                                                        date, in_hand_records)

        # Handle Ethnicity counts
        cls.prepare_key_value_count_for_single_question(ETHNICITY_QUESTION_CODE, cls.ethnicity_counts, from_time,
                                                        to_time, date, in_hand_records)

        # Handle Marital status counts
        cls.prepare_key_value_count_for_single_question(MARITAL_STATUS_QUESTION_CODE, cls.marital_status_counts,
                                                        from_time,
                                                        to_time, date, in_hand_records)

        # Handle Education counts
        cls.prepare_key_value_count_for_single_question(EDUCATION_QUESTION_CODE, cls.education_counts, from_time,
                                                        to_time, date, in_hand_records)

        # Handle Employment counts
        cls.prepare_key_value_count_for_single_question(EMPLOYMENT_QUESTION_CODE, cls.employment_counts, from_time,
                                                        to_time, date, in_hand_records)

        # Handle Difficulty in Seeing counts
        cls.prepare_key_value_count_for_single_question(
            DIFFICULTY_IN_SEEING_QUESTION_CODE, cls.difficulty_in_seeing_counts,
            from_time, to_time, date, in_hand_records)

        # Handle Difficulty in Hearing counts
        cls.prepare_key_value_count_for_single_question(
            DIFFICULTY_IN_HEARING_QUESTION_CODE, cls.difficulty_in_hearing_counts,
            from_time, to_time, date, in_hand_records)

        # Handle Difficulty in Walking counts
        cls.prepare_key_value_count_for_single_question(
            DIFFICULTY_IN_WALKING_QUESTION_CODE, cls.difficulty_in_walking_counts,
            from_time, to_time, date, in_hand_records)

        # Handle Difficulty in Remembering counts
        cls.prepare_key_value_count_for_single_question(
            DIFFICULTY_IN_REMEMBERING_QUESTION_CODE, cls.difficulty_in_remembering_counts,
            from_time, to_time, date, in_hand_records)

        # Handle Difficulty in Self Care counts
        cls.prepare_key_value_count_for_single_question(
            DIFFICULTY_IN_SELF_CARE_QUESTION_CODE, cls.difficulty_in_self_care_counts,
            from_time, to_time, date, in_hand_records)

        # Handle Difficulty in Communicating counts
        cls.prepare_key_value_count_for_single_question(
            DIFFICULTY_IN_COMMUNICATING_QUESTION_CODE, cls.difficulty_in_communicating_counts,
            from_time, to_time, date, in_hand_records)

        # Handle disability counts
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

            record = cls.get_record(
                date=date, from_time=from_time, to_time=to_time, ward_id=ward_id, city_id=city_id,
                in_hand_records=in_hand_records)

            # Check if this key-value pair already exists or not
            label = PG_DISABILITY_LABEL_DICT[q['question__question_code']] \
                if q['question__question_code'] in PG_DISABILITY_LABEL_DICT.keys() else \
                q['question__question_code']
            key_value_count = record.disability_counts.filter(label=label).first()

            # Update (or create) the count
            if key_value_count is None:
                key_value_count = KeyValueCount(label=label, count=q['count'])
            else:
                key_value_count.count = q['count']
            key_value_count.save()
            record.disability_counts.add(key_value_count)

        # Handle HH Gender counts
        cls.prepare_key_value_count_for_single_question(HH_GENDER_QUESTION_CODE, cls.hh_gender_counts, from_time,
                                                        to_time, date, in_hand_records)
        # Handle HH Employment counts
        cls.prepare_key_value_count_for_single_question(HH_EMPLOYMENT_QUESTION_CODE, cls.hh_employment_counts,
                                                        from_time, to_time, date, in_hand_records)
        # Handle HH Education counts
        cls.prepare_key_value_count_for_single_question(HH_EDUCATION_QUESTION_CODE, cls.hh_education_counts,
                                                        from_time, to_time, date, in_hand_records)

        # Handle HH Difficulty in Seeing counts
        cls.prepare_key_value_count_for_single_question(
            HH_DIFFICULTY_IN_SEEING_QUESTION_CODE, cls.hh_difficulty_in_seeing_counts,
            from_time, to_time, date, in_hand_records)

        # Handle HH Difficulty in Hearing counts
        cls.prepare_key_value_count_for_single_question(
            HH_DIFFICULTY_IN_HEARING_QUESTION_CODE, cls.hh_difficulty_in_hearing_counts,
            from_time, to_time, date, in_hand_records)

        # Handle HH Difficulty in Walking counts
        cls.prepare_key_value_count_for_single_question(
            HH_DIFFICULTY_IN_WALKING_QUESTION_CODE, cls.hh_difficulty_in_walking_counts,
            from_time, to_time, date, in_hand_records)

        # Handle HH Difficulty in Remembering counts
        cls.prepare_key_value_count_for_single_question(
            HH_DIFFICULTY_IN_REMEMBERING_QUESTION_CODE, cls.hh_difficulty_in_remembering_counts,
            from_time, to_time, date, in_hand_records)

        # Handle HH Difficulty in Self Care counts
        cls.prepare_key_value_count_for_single_question(
            HH_DIFFICULTY_IN_SELF_CARE_QUESTION_CODE, cls.hh_difficulty_in_self_care_counts,
            from_time, to_time, date, in_hand_records)

        # Handle HH Difficulty in Communicating counts
        cls.prepare_key_value_count_for_single_question(
            HH_DIFFICULTY_IN_COMMUNICATING_QUESTION_CODE, cls.hh_difficulty_in_communicating_counts,
            from_time, to_time, date, in_hand_records)

        # Handle hh disability counts
        question_responses = QuestionResponse.objects.filter(
            section_response__survey_response__survey__name__icontains=PG_MEMBER_SURVEY_NAME,
            section_response__survey_response__date_created__gte=from_time,
            section_response__survey_response__date_created__lte=to_time,
            question__question_code__in=HH_DISABLITY_QUESTION_CODE,
            answer_text__in=HH_DISABLED_ANSWER_TEXT
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

            record = cls.get_record(
                date=date, from_time=from_time, to_time=to_time, ward_id=ward_id, city_id=city_id,
                in_hand_records=in_hand_records)

            # Check if this key-value pair already exists or not
            label = HH_DISABILITY_LABEL_DICT[q['question__question_code']] \
                if q['question__question_code'] in HH_DISABILITY_LABEL_DICT.keys() else q['question__question_code']
            key_value_count = record.hh_disability_counts.filter(label=label).first()

            # Update (or create) the count
            if key_value_count is None:
                key_value_count = KeyValueCount(label=label, count=q['count'])
            else:
                key_value_count.count = q['count']
            key_value_count.save()
            record.hh_disability_counts.add(key_value_count)

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

            record = cls.get_record(
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

            record = cls.get_record(
                date=date, from_time=from_time, to_time=to_time, ward_id=ward_id, city_id=city_id,
                in_hand_records=in_hand_records)

            record.pg_member_no_difficulty_counts = q['count']
            record.save()

    @classmethod
    def prepare_key_value_count_for_single_question(cls, question_code, m2m_descripter, from_time, to_time, date,
                                                    in_hand_records):
        question_responses = QuestionResponse.objects.filter(
            section_response__survey_response__survey__name__icontains=PG_MEMBER_SURVEY_NAME,
            section_response__survey_response__date_created__gte=from_time,
            section_response__survey_response__date_created__lte=to_time,
            question__question_code=question_code
        ).values(
            'answer_text',
            'section_response__survey_response__respondent_client__assigned_to__parent__address__geography_id',
            'section_response__survey_response__respondent_client__assigned_to__parent__address__geography__parent_id'
        ).annotate(
            count=Count('pk', distinct=True)
        )
        for q in question_responses:
            ward_id = q[
                'section_response__survey_response__respondent_client__assigned_to__parent__address__geography_id']
            city_id = q[
                'section_response__survey_response__respondent_client__assigned_to__parent__address__geography__parent_id']

            record = cls.get_record(
                date=date, from_time=from_time, to_time=to_time, ward_id=ward_id, city_id=city_id,
                in_hand_records=in_hand_records)

            # Check if this key-value pair already exists or not
            m2m_manager = getattr(record, m2m_descripter.field.name)
            key_value_count = m2m_manager.filter(label=q['answer_text']).first()

            # Update (or create) the count
            if key_value_count is None:
                key_value_count = KeyValueCount(label=q['answer_text'], count=q['count'])
            else:
                key_value_count.count = q['count']
            key_value_count.save()
            m2m_manager.add(key_value_count)

    @classmethod
    def prepare_hm_key_value_for_single_question(cls, hm_field, question_code, from_time, to_time, date,
                                                 in_hand_records):
        question_responses = QuestionResponse.objects.filter(
            section_response__survey_response__survey__name__icontains=PG_MEMBER_SURVEY_NAME,
            section_response__survey_response__date_created__gte=from_time,
            section_response__survey_response__date_created__lte=to_time,
            question__question_code=question_code
        ).exclude(answer_text='').exclude(answer_text__isnull=True).values(
            'section_response__survey_response__respondent_client__assigned_to__parent__address__geography_id',
            'section_response__survey_response__respondent_client__assigned_to__parent__address__geography__parent_id'
        ).annotate(
            total=Sum(Cast('answer_text', IntegerField()))
        )
        for q in question_responses:
            ward_id = q[
                'section_response__survey_response__respondent_client__assigned_to__parent__address__geography_id']
            city_id = q[
                'section_response__survey_response__respondent_client__assigned_to__parent__address__geography__parent_id']

            record = cls.get_record(
                date=date, from_time=from_time, to_time=to_time, ward_id=ward_id, city_id=city_id,
                in_hand_records=in_hand_records)

            _hm_field = hm_field.field_name
            setattr(record, _hm_field, q['total'])
            record.save()

    @classmethod
    def prepare_yes_answer_frequency_count(cls, model_field, question_code, from_time, to_time, date, in_hand_records):
        question_responses = QuestionResponse.objects.filter(
            section_response__survey_response__survey__name__icontains=PG_MEMBER_SURVEY_NAME,
            section_response__survey_response__date_created__gte=from_time,
            section_response__survey_response__date_created__lte=to_time,
            question__question_code=question_code, answer_text='Yes'
        ).values(
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

            record = cls.get_record(
                date=date, from_time=from_time, to_time=to_time, ward_id=ward_id, city_id=city_id,
                in_hand_records=in_hand_records)

            _model_field = model_field.field_name
            setattr(record, _model_field, q['count'])
            record.save()

    @classmethod
    def prepare_no_answer_frequency_count(cls, model_field, question_code, from_time, to_time, date, in_hand_records):
        question_responses = QuestionResponse.objects.filter(
            section_response__survey_response__survey__name__icontains=PG_MEMBER_SURVEY_NAME,
            section_response__survey_response__date_created__gte=from_time,
            section_response__survey_response__date_created__lte=to_time,
            question__question_code=question_code, answer_text='No'
        ).values(
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

            record = cls.get_record(
                date=date, from_time=from_time, to_time=to_time, ward_id=ward_id, city_id=city_id,
                in_hand_records=in_hand_records)

            _model_field = model_field.field_name
            setattr(record, _model_field, q['count'])
            record.save()
