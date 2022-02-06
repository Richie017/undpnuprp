import sys

from django.db import models

from blackwidow.core.models.contracts.base import DomainEntity
from blackwidow.engine.extensions.console_debug import bw_debug
from undp_nuprp.reports.config.constants.pg_survey_constants import EDUCATION_ATAINMENT_QUESTION_CODE, \
    SCHOOL_ATTENDENCE_QUESTION_CODE, CHILD_BIRTH_QUESTION_CODE, \
    ANY_DISABLED_MEMBER_QUESTION_CODE, HH_RESOURCE_QUESTION_CODE, SANITATION_SHARED_QUESTION_CODE, \
    SANITATION_QUALITY_QUESTION_CODE, POOR_SANITATION_ANSWERS, WATER_COLLECTION_TIME_QUESTION_CODE, WATER_FETCHING_TIME, \
    WATER_SOURCE_QUESTION_CODE, FLOOR_TYPE_QUESTION_CODE, FUEL_TYPE_QUESTION_CODE, POOR_FUEL_ANSWERS, \
    HIGH_VALUE_RESOURCES, CAR_TRUCK_RESOURCE
from undp_nuprp.reports.config.constants.values import BATCH_SIZE
from undp_nuprp.survey.models.entity.answer import Answer
from undp_nuprp.survey.models.response.question_response import QuestionResponse
from undp_nuprp.survey.models.response.survey_response import SurveyResponse

__author__ = 'Shuvro'


class PGPovertyIndexShortListedGrantee(DomainEntity):
    survey_response = models.ForeignKey('survey.SurveyResponse', null=True)
    index_no = models.IntegerField(default=0)
    index_name = models.CharField(max_length=256, blank=True)
    index_description = models.TextField(blank=True, null=True)
    is_deprived = models.BooleanField(default=True)
    score = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        super(PGPovertyIndexShortListedGrantee, self).save(*args, **kwargs)
        bw_debug("%s deprives: %d - %s"
                 % (self.survey_response.code, self.index_no, self.index_name))

    @classmethod
    def generate(cls, batch_count=None, batch_size=BATCH_SIZE):

        to_be_handled = SurveyResponse.objects.filter(
            shortlistedeligiblegrantee__isnull=False,
            pgpovertyindexshortlistedgrantee__isnull=True).distinct('pk').count()

        if batch_count is None:
            batch_count = sys.maxsize
        batch = 0
        total_handled = 0
        while batch < batch_count:
            batch += 1
            print('Handling batch #{}: {}/{}'.format(batch, total_handled + batch_size, to_be_handled))
            handled = cls.handle_mpi_calculation(batch_size=batch_size)
            total_handled += handled
            if handled < batch_size or total_handled > to_be_handled:
                break

    @classmethod
    def handle_mpi_calculation(cls, batch_size=BATCH_SIZE):
        candidate_responses = SurveyResponse.objects.filter(
            shortlistedeligiblegrantee__isnull=False,
            pgpovertyindexshortlistedgrantee__isnull=True).distinct('pk').order_by(
            'pk')[:batch_size]

        poverty_indices = list()
        for response in candidate_responses:
            mpi_score = 0
            index = 1
            primary_group_member = response.respondent_client

            if primary_group_member:
                # For "Has any member of the primary_group_member completed 5 years of schooling or more?" -> "No" 16.7
                mpi_query = QuestionResponse.objects.filter(
                    question__question_code=EDUCATION_ATAINMENT_QUESTION_CODE,
                    section_response__survey_response_id=response.pk).last()
                if mpi_query and mpi_query.answer_text.lower() == 'no':
                    mpi_score += 16.7
                    poverty_index = cls(
                        survey_response_id=response.pk, index_no=index,
                        index_name='Education (Years of Schooling)',
                        index_description='No primary_group_member member has completed five years of schooling'
                    )
                    poverty_indices.append(poverty_index)
                index += 1

                # For "Any school-aged child is attending school in years 1 to 8" -> "No" 16.7
                mpi_query = QuestionResponse.objects.filter(
                    question__question_code=SCHOOL_ATTENDENCE_QUESTION_CODE,
                    section_response__survey_response_id=response.pk).last()
                if mpi_query and mpi_query.answer_text.lower() == 'no':
                    mpi_score += 16.7
                    poverty_index = cls(
                        survey_response_id=response.pk, index_no=index,
                        index_name='Education (Child School Attendance)',
                        index_description='Any school-aged child is not attending school in years 5 to 18'
                    )
                    poverty_indices.append(poverty_index)
                index += 1

                # For "Has the adult head of the family ever given birth to a son or daughter who was born alive but later died, between 0-5 years" -> "Yes" 16.7
                mpi_query = QuestionResponse.objects.filter(
                    question__question_code=CHILD_BIRTH_QUESTION_CODE,
                    section_response__survey_response_id=response.pk).last()
                if mpi_query and mpi_query.answer_text.lower() == 'yes':
                    mpi_score += 16.7
                    poverty_index = cls(
                        survey_response_id=response.pk, index_no=index,
                        index_name='Health (Mortality)',
                        index_description='Any child has died in the family'
                    )
                    poverty_indices.append(poverty_index)
                index += 1

                # For "Is the household head of the family disabled" -> "Yes" 16.7
                mpi_query = QuestionResponse.objects.filter(
                    question__question_code=ANY_DISABLED_MEMBER_QUESTION_CODE,
                    section_response__survey_response_id=response.pk).last()
                if mpi_query and mpi_query.answer_text.lower() == 'yes':
                    mpi_score += 16.7
                    poverty_index = cls(
                        survey_response_id=response.pk, index_no=index, index_name='Disability',
                        index_description='Household head is disabled'
                    )
                    poverty_indices.append(poverty_index)
                index += 1

                # For "The household has no electricity" 5.5
                mpi_query = QuestionResponse.objects.filter(
                    question__question_code=HH_RESOURCE_QUESTION_CODE,
                    section_response__survey_response_id=response.pk,
                    answer_text__iexact='Electricity').last()
                if not mpi_query:
                    mpi_score += 5.5
                    poverty_index = cls(
                        survey_response_id=response.pk, index_no=index,
                        index_name='Standard of Living (Electricity)',
                        index_description='The household has no electricity'
                    )
                    poverty_indices.append(poverty_index)
                index += 1

                # For "Sanitation not improved" 5.5
                mpi_query = QuestionResponse.objects.filter(
                    question__question_code=SANITATION_SHARED_QUESTION_CODE,
                    section_response__survey_response_id=response.pk,
                    answer_text__iexact='yes').last()
                if mpi_query:
                    mpi_score += 5.5
                    poverty_index = cls(
                        survey_response_id=response.pk, index_no=index,
                        index_name='Standard of Living (Sanitation)',
                        index_description='The household\'s sanitation facility is not improved (according to MDG guidelines), or it is improved but shared with other households. If the HH has the following sanitation facility then it is not improved: pit latrine without slab/ open pit, bucket, hanging toilet, no facilities or bush/ field'
                    )
                    poverty_indices.append(poverty_index)
                else:
                    answers = Answer.objects.filter(
                        question__question_code=SANITATION_QUALITY_QUESTION_CODE).filter(
                        text__in=POOR_SANITATION_ANSWERS).values_list('id', flat=True)
                    mpi_query = QuestionResponse.objects.filter(
                        question__question_code=SANITATION_QUALITY_QUESTION_CODE,
                        section_response__survey_response_id=response.pk,
                        answer_id__in=answers).first()
                    if mpi_query:
                        mpi_score += 5.5
                        poverty_index = cls(
                            survey_response_id=response.pk, index_no=index,
                            index_name='Standard of Living (Sanitation)',
                            index_description='The household\'s sanitation facility is not improved (according to MDG guidelines), or it is improved but shared with other households. If the HH has the following sanitation facility then it is not improved: pit latrine without slab/ open pit, bucket, hanging toilet, no facilities or bush/ field'
                        )
                        poverty_indices.append(poverty_index)
                index += 1

                # For "No access of drinking water" 5.5
                mpi_query = QuestionResponse.objects.filter(
                    question__question_code=WATER_COLLECTION_TIME_QUESTION_CODE,
                    section_response__survey_response_id=response).first()
                water_deprived_decided = False
                if mpi_query:
                    try:
                        minutes = mpi_query.answer_text
                        if minutes == WATER_FETCHING_TIME:
                            mpi_score += 5.5
                            poverty_index = cls(
                                survey_response_id=response.pk, index_no=index,
                                index_name='Standard of Living (Water)',
                                index_description='The household does not have access to clean drinking water (according to MDG guidelines), or clean water is more than 30 minutes walking from home If they access water from: rainwater, tanker truck, cart with small tank/ drum, surface water, unprotected well, unprotected spring, then they do not have access to clean water'
                            )
                            poverty_indices.append(poverty_index)
                            water_deprived_decided = True
                    except:
                        pass
                if not water_deprived_decided:
                    answers = Answer.objects.filter(
                        question__question_code=WATER_SOURCE_QUESTION_CODE).filter(
                        text__in=['Rainwater', 'Tanker-truck', 'Cart with small tank/drum',
                                  'Surface water (river, stream, dam, lake, pond, canal, irrigation channel)',
                                  'Unprotected spring', 'Unprotected well', 'Other']).values_list('id', flat=True)
                    mpi_query = QuestionResponse.objects.filter(
                        question__question_code=WATER_SOURCE_QUESTION_CODE,
                        section_response__survey_response_id=response.pk,
                        answer_id__in=answers
                    ).first()
                    if mpi_query:
                        mpi_score += 5.5
                        poverty_index = cls(
                            survey_response_id=response.pk, index_no=index,
                            index_name='Standard of Living (Water)',
                            index_description='The household does not have access to clean drinking water (according to MDG guidelines), or clean water is more than 30 minutes walking from home If they access water from: rainwater, tanker truck, cart with small tank/ drum, surface water, unprotected well, unprotected spring, then they do not have access to clean water'
                        )
                        poverty_indices.append(poverty_index)
                index += 1

                # For "The household has dirt, sand or dung floor" 5.5
                answers = Answer.objects.filter(
                    question__question_code=FLOOR_TYPE_QUESTION_CODE).filter(
                    text__in=['Earth/sand/semi pucca floor', 'Dung', 'Other']).values_list('id', flat=True)
                mpi_query = QuestionResponse.objects.filter(
                    question__question_code=FLOOR_TYPE_QUESTION_CODE,
                    section_response__survey_response_id=response.pk,
                    answer_id__in=answers
                ).first()
                if mpi_query:
                    mpi_score += 5.5
                    poverty_index = cls(
                        survey_response_id=response.pk, index_no=index,
                        index_name='Standard of Living (Floor)',
                        index_description='The household has dirt, sand or dung floor'
                    )
                    poverty_indices.append(poverty_index)
                index += 1

                # For "The household cooks with dung, wood or charcoal" 5.5
                answers = Answer.objects.filter(
                    question__question_code=FUEL_TYPE_QUESTION_CODE).filter(
                    text__in=POOR_FUEL_ANSWERS).values_list('id', flat=True)
                mpi_query = QuestionResponse.objects.filter(
                    question__question_code=FUEL_TYPE_QUESTION_CODE,
                    section_response__survey_response_id=response.pk,
                    answer_id__in=answers
                ).first()
                if mpi_query:
                    mpi_score += 5.5
                    poverty_index = cls(
                        survey_response_id=response.pk, index_no=index,
                        index_name='Standard of Living (Cooking Fuel)',
                        index_description='The household cooks with dung, wood or charcoal'
                    )
                    poverty_indices.append(poverty_index)
                index += 1

                # PG member is considered poor if they have 1 high resource value
                # and rich if they have more than 1 high resource and 1 car resource
                no_more_than_one = QuestionResponse.objects.filter(
                    question__question_code=HH_RESOURCE_QUESTION_CODE,
                    section_response__survey_response_id=response.pk,
                    answer_text__in=HIGH_VALUE_RESOURCES
                ).count()
                if not no_more_than_one > 1:
                    none_of_this = QuestionResponse.objects.filter(
                        question__question_code=HH_RESOURCE_QUESTION_CODE,
                        section_response__survey_response_id=response.pk,
                        answer_text__in=CAR_TRUCK_RESOURCE
                    ).count()
                    if not none_of_this:
                        mpi_score += 5.5
                        poverty_index = cls(
                            survey_response_id=response.pk, index_no=index,
                            index_name='Standard of Living (Assets)',
                            index_description='The household does not own more than one of: radio, TV, telephone, bike, motorbike or refrigerator, and does not'
                        )
                        poverty_indices.append(poverty_index)

        cls.objects.bulk_create(poverty_indices)
        return candidate_responses.count()
