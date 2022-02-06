from datetime import datetime

from django.db import models
from django.db.models.aggregates import Max

from undp_nuprp.reports.config.constants.values import BATCH_SIZE
from undp_nuprp.reports.models.base.cache.cache_base import CacheBase
from undp_nuprp.survey.models.response.question_response import QuestionResponse

__author__ = "Tareq, Shama"

cached_question_codes = [
    '1.5', '1.9.', '1.8', '2.4', '2.5', '2.6', '2.1'
]


class QuestionResponseCache(CacheBase):
    day = models.IntegerField(default=1, db_index=True)
    month = models.IntegerField(default=1, db_index=True)
    year = models.IntegerField(default=2010, db_index=True)
    ref_time = models.BigIntegerField(default=0, db_index=True)
    survey_count = models.IntegerField(default=0)

    division = models.ForeignKey('core.Geography', related_name='question_division')
    city = models.ForeignKey('core.Geography', related_name='question_city', db_index=True)
    ward = models.ForeignKey('core.Geography', related_name='question_ward', db_index=True)
    mahalla = models.ForeignKey('core.Geography', related_name='question_mahalla')
    poor_settlement = models.ForeignKey('core.Geography', related_name='question_poor_settlement')
    city_name = models.CharField(max_length=128, blank=True, db_index=True)

    survey_response = models.ForeignKey('survey.SurveyResponse')
    section_response = models.ForeignKey('survey.SectionResponse')
    question = models.ForeignKey('survey.Question')
    question_code = models.CharField(default='', max_length=200, db_index=True)
    question_text = models.CharField(max_length=1024, blank=True)
    answer = models.ForeignKey('survey.Answer')
    answer_text = models.CharField(max_length=2048, blank=True, db_index=True)

    @classmethod
    def generate(cls, number_of_batches=None, batch_size=BATCH_SIZE):
        batch_number = 0
        if number_of_batches is None:
            while True:
                processed_count = cls.cache_intervaled_report(batch_size=batch_size)
                batch_number += 1
                print("Number of responses processed %d batch number %d"
                      % (processed_count, batch_number))
                if processed_count < batch_size:
                    break

        else:
            while True:
                processed_count = cls.cache_intervaled_report(batch_size=batch_size)
                batch_number += 1
                print("Number of responses processed %d batch number %d"
                      % (processed_count, batch_number))
                if processed_count < batch_size or batch_number == number_of_batches:
                    break

    @classmethod
    def cache_intervaled_report(cls, batch_size=BATCH_SIZE):
        creatable_cache = list()
        updatable_cache = list()

        in_hand_records = dict()

        object_id = None
        survey_time = 0

        last_handled_survey_id = cls.objects.aggregate(Max('object_id'))['object_id__max']
        last_handled_survey_id = last_handled_survey_id if last_handled_survey_id else 0

        surveys = QuestionResponse.objects.order_by('pk').filter(
            question__question_code__in=cached_question_codes).filter(
            pk__gt=last_handled_survey_id)[:batch_size].values(
            'pk', 'organization_id', 'answer_text',
            'section_response__survey_response__address__geography_id',  # poor_settlement_id
            'section_response__survey_response__address__geography__parent_id',  # mahalla_id
            'section_response__survey_response__address__geography__parent__parent_id',  # ward_id
            'section_response__survey_response__address__geography__parent__parent__parent_id',  # city_id
            'section_response__survey_response__address__geography__parent__parent__parent__name',  # city_name
            'section_response__survey_response__address__geography__parent__parent__parent__parent_id',  # division_id
            'question_id', 'answer_id', 'question__question_code', 'section_response__survey_response__survey_time',
            'question_text', 'section_response__survey_response_id', 'section_response_id')

        for entry in surveys:
            object_id = entry['pk']
            organization_id = entry['organization_id']
            poor_settlement_id = entry['section_response__survey_response__address__geography_id']
            mahalla_id = entry['section_response__survey_response__address__geography__parent_id']
            ward_id = entry['section_response__survey_response__address__geography__parent__parent_id']
            city_id = entry['section_response__survey_response__address__geography__parent__parent__parent_id']
            city_name = entry['section_response__survey_response__address__geography__parent__parent__parent__name']
            division_id = entry[
                'section_response__survey_response__address__geography__parent__parent__parent__parent_id']
            survey_time = entry['section_response__survey_response__survey_time']
            question_code = entry['question__question_code']
            question_id = entry['question_id']
            answer_id = entry['answer_id']
            survey_response_id = entry['section_response__survey_response_id']
            section_response_id = entry['section_response_id']
            question_text = entry['question_text']
            answer_text = entry['answer_text']

            survey_datetime = datetime.fromtimestamp(survey_time / 1000)
            survey_year = survey_datetime.year
            survey_month = survey_datetime.month
            survey_day = survey_datetime.day
            survey_date = survey_datetime.date()

            if (survey_date, poor_settlement_id, question_id, answer_id) not in in_hand_records.keys():
                record = cls.objects.filter(year=survey_year, month=survey_month, day=survey_day,
                                            poor_settlement_id=poor_settlement_id, question_id=question_id,
                                            answer_id=answer_id).first()
                if record is None:
                    record = cls(organization_id=organization_id, year=survey_year, month=survey_month, day=survey_day,
                                 poor_settlement_id=poor_settlement_id, mahalla_id=mahalla_id, ward_id=ward_id,
                                 city_id=city_id, division_id=division_id, city_name=city_name,
                                 survey_response_id=survey_response_id, section_response_id=section_response_id,
                                 question_id=question_id, question_code=question_code, question_text=question_text,
                                 answer_id=answer_id, answer_text=answer_text, ref_time=survey_time)
                    creatable_cache.append(record)
                else:
                    updatable_cache.append(record)
                in_hand_records[(survey_date, poor_settlement_id, question_id, answer_id)] = record
            else:
                record = in_hand_records[(survey_date, poor_settlement_id, question_id, answer_id)]

            timestamp_now = datetime.now().timestamp() * 1000
            record.last_updated = timestamp_now
            record.date_created = timestamp_now
            record.object_id = object_id
            record.survey_count += 1

        if len(creatable_cache) > 0:
            print('Creating %d new enties between object %d and object %d upto %s' % (len(creatable_cache),
                                                                                      last_handled_survey_id + 1,
                                                                                      object_id, datetime.fromtimestamp(
                survey_time / 1000)))
            cls.objects.bulk_create(creatable_cache)
            print('...Created')

        if len(updatable_cache) > 0:
            print('Updating %d enties between object %d and object %d upto %s' % (len(updatable_cache),
                                                                                  last_handled_survey_id + 1,
                                                                                  object_id, datetime.fromtimestamp(
                survey_time / 1000)))
            cls.objects.bulk_update(updatable_cache)
            print('...Created')

        return surveys.count()
