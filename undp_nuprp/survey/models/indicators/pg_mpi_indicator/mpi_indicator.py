import sys

from django.db import models

from blackwidow.core.models.organizations.organization import Organization
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.config.constants.pg_survey_constants import *
from undp_nuprp.reports.config.constants.values import *
from undp_nuprp.reports.models.base.cache.cache_base import CacheBase
from undp_nuprp.survey.models.entity.answer import Answer
from undp_nuprp.survey.models.indicators.pg_mpi_indicator.poverty_index import PGPovertyIndex
from undp_nuprp.survey.models.response.question_response import QuestionResponse
from undp_nuprp.survey.models.response.survey_response import SurveyResponse

__author__ = 'Tareq'


class PGMPIIndicator(CacheBase):
    survey_response = models.ForeignKey('survey.SurveyResponse')
    primary_group_member = models.ForeignKey('nuprp_admin.PrimaryGroupMember', null=True)
    is_female_headed = models.BooleanField(default=False)
    is_male_headed = models.BooleanField(default=False)
    is_head_disabled = models.BooleanField(default=False)
    is_minority = models.BooleanField(default=False)
    mpi_score = models.FloatField(default=0)

    @classmethod
    def generate(cls, batch_count=None, batch_size=BATCH_SIZE):
        to_be_handled = SurveyResponse.objects.using(
            BWDatabaseRouter.get_read_database_name()
        ).filter(survey__name='PG Member Survey Questionnaire', pgmpiindicator__isnull=True).count()

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
        cls.clear_mpi_indicators_of_deleted_members()

    @classmethod
    def clear_mpi_indicators_of_deleted_members(cls):
        print("Deleting MPI Indicators of deleted members...")
        deletable_mpi_scores = PGMPIIndicator.objects.filter(
            primary_group_member__is_deleted=True) | PGMPIIndicator.objects.filter(primary_group_member__isnull=True)
        deletable_mpi_scores.delete()
        print("...Deleted")

    @classmethod
    def handle_mpi_calculation(cls, batch_size=BATCH_SIZE):
        candidate_responses = SurveyResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
            survey__name='PG Member Survey Questionnaire', pgmpiindicator__isnull=True).order_by('pk')[:batch_size]

        creatable_mpi_list = list()
        poverty_indices = list()

        organization_id = Organization.get_organization_from_cache().pk

        for response in candidate_responses:
            mpi_indicator, poverty_indices = cls.get_mpi_indicator_object_for_survey_response(
                response=response, organization_id=organization_id, poverty_indices=poverty_indices)
            creatable_mpi_list.append(mpi_indicator)

        PGPovertyIndex.objects.using(BWDatabaseRouter.get_write_database_name()).bulk_create(poverty_indices)
        PGMPIIndicator.objects.using(BWDatabaseRouter.get_write_database_name()).bulk_create(creatable_mpi_list)
        return candidate_responses.count()

    @classmethod
    def get_mpi_indicator_object_for_survey_response(cls, response, organization_id, poverty_indices):
        mpi_score = 0
        index = 1
        primary_group_member = response.respondent_client
        mpi_indicator = None

        if primary_group_member:
            old_poverty_indices = PGPovertyIndex(primary_group_member_id=primary_group_member.pk)
            # is female headed
            is_female_headed = False
            female_response = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                section_response__survey_response_id=response.pk, question__question_code=HH_GENDER_QUESTION_CODE
            ).values('answer_text').first()

            if female_response is None:
                female_response = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                    section_response__survey_response_id=response.pk, question__question_code=GENDER_QUESTION_CODE,
                    answer_text__iexact='Female').first()
            else:
                female_response = (female_response['answer_text'].lower() == 'female')
            if female_response:
                is_female_headed = True

            is_male_headed = False
            male_response = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                section_response__survey_response_id=response.pk, question__question_code=HH_GENDER_QUESTION_CODE
            ).values('answer_text').first()
            if male_response is None:
                male_response = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                    section_response__survey_response_id=response.pk, question__question_code=GENDER_QUESTION_CODE,
                    answer_text__iexact='Male').first()
            else:
                male_response = (male_response['answer_text'].lower() == 'male')
            if male_response:
                is_male_headed = True

            # is disabled
            is_head_disabled = False
            disabled_response = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                section_response__survey_response_id=response.pk,
                question__question_code__in=DISABLITY_QUESTION_CODE,
                answer_text__in=DISABLED_ANSWER_TEXT).first()
            if disabled_response:
                is_head_disabled = True

            # is minority
            is_minority = False
            bengali_response = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                section_response__survey_response_id=response.pk, question__question_code=ETHNICITY_QUESTION_CODE,
                answer_text__iexact=ETHNIC_MAJORITY_ANSWER).first()
            if bengali_response:
                is_minority = True

            # For "Has any member of the primary_group_member completed 5 years of schooling or more?" -> "No" 16.7
            mpi_query = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                question__question_code=EDUCATION_ATAINMENT_QUESTION_CODE,
                section_response__survey_response_id=response.pk).last()
            if mpi_query and mpi_query.answer_text.lower() == 'no':
                mpi_score += 16.7
                poverty_index = PGPovertyIndex(
                    primary_group_member_id=primary_group_member.pk, index_no=index,
                    index_name='Education (Years of Schooling)',
                    index_description='No primary_group_member member has completed five years of schooling'
                )
                poverty_indices.append(poverty_index)
            index += 1

            # For "Any school-aged child is attending school in years 1 to 8" -> "No" 16.7
            mpi_query = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                question__question_code=SCHOOL_ATTENDENCE_QUESTION_CODE,
                section_response__survey_response_id=response.pk).last()
            if mpi_query and mpi_query.answer_text.lower() == 'no':
                mpi_score += 16.7
                poverty_index = PGPovertyIndex(
                    primary_group_member_id=primary_group_member.pk, index_no=index,
                    index_name='Education (Child School Attendance)',
                    index_description='Any school-aged child is not attending school in years 5 to 18'
                )
                poverty_indices.append(poverty_index)
            index += 1

            # For "Has the adult head of the family ever given birth to a son or daughter who was born alive but later died, between 0-5 years" -> "Yes" 16.7
            mpi_query = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                question__question_code=CHILD_BIRTH_QUESTION_CODE,
                section_response__survey_response_id=response.pk).last()
            if mpi_query and mpi_query.answer_text.lower() == 'yes':
                mpi_score += 16.7
                poverty_index = PGPovertyIndex(
                    primary_group_member_id=primary_group_member.pk, index_no=index,
                    index_name='Health (Mortality)',
                    index_description='Any child has died in the family'
                )
                poverty_indices.append(poverty_index)
            index += 1

            # For "Is the household head of the family disabled" -> "Yes" 16.7
            mpi_query = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                question__question_code=ANY_DISABLED_MEMBER_QUESTION_CODE,
                section_response__survey_response_id=response.pk).last()
            if mpi_query and mpi_query.answer_text.lower() == 'yes':
                mpi_score += 16.7
                poverty_index = PGPovertyIndex(
                    primary_group_member_id=primary_group_member.pk, index_no=index, index_name='Disability',
                    index_description='Household head is disabled'
                )
                poverty_indices.append(poverty_index)
            index += 1

            # For "The household has no electricity" 5.5
            mpi_query = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                question__question_code=HH_RESOURCE_QUESTION_CODE,
                section_response__survey_response_id=response.pk,
                answer_text__iexact='Electricity').last()
            if not mpi_query:
                mpi_score += 5.5
                poverty_index = PGPovertyIndex(
                    primary_group_member_id=primary_group_member.pk, index_no=index,
                    index_name='Standard of Living (Electricity)',
                    index_description='The household has no electricity'
                )
                poverty_indices.append(poverty_index)
            index += 1

            # For "Sanitation not improved" 5.5
            mpi_query = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                question__question_code=SANITATION_SHARED_QUESTION_CODE,
                section_response__survey_response_id=response.pk,
                answer_text__iexact='yes').last()
            if mpi_query:
                mpi_score += 5.5
                poverty_index = PGPovertyIndex(
                    primary_group_member_id=primary_group_member.pk, index_no=index,
                    index_name='Standard of Living (Sanitation)',
                    index_description='The household\'s sanitation facility is not improved (according to MDG guidelines), or it is improved but shared with other households. If the HH has the following sanitation facility then it is not improved: pit latrine without slab/ open pit, bucket, hanging toilet, no facilities or bush/ field'
                )
                poverty_indices.append(poverty_index)
            else:
                answers = Answer.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                    question__question_code=SANITATION_QUALITY_QUESTION_CODE).filter(
                    text__in=POOR_SANITATION_ANSWERS).values_list('id', flat=True)
                mpi_query = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                    question__question_code=SANITATION_QUALITY_QUESTION_CODE,
                    section_response__survey_response_id=response.pk,
                    answer_id__in=answers).first()
                if mpi_query:
                    mpi_score += 5.5
                    poverty_index = PGPovertyIndex(
                        primary_group_member_id=primary_group_member.pk, index_no=index,
                        index_name='Standard of Living (Sanitation)',
                        index_description='The household\'s sanitation facility is not improved (according to MDG guidelines), or it is improved but shared with other households. If the HH has the following sanitation facility then it is not improved: pit latrine without slab/ open pit, bucket, hanging toilet, no facilities or bush/ field'
                    )
                    poverty_indices.append(poverty_index)
            index += 1

            # For "No access of drinking water" 5.5
            mpi_query = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                question__question_code=WATER_COLLECTION_TIME_QUESTION_CODE,
                section_response__survey_response_id=response).first()
            water_deprived_decided = False
            if mpi_query:
                try:
                    minutes = mpi_query.answer_text
                    if minutes == WATER_FETCHING_TIME:
                        mpi_score += 5.5
                        poverty_index = PGPovertyIndex(
                            primary_group_member_id=primary_group_member.pk, index_no=index,
                            index_name='Standard of Living (Water)',
                            index_description='The household does not have access to clean drinking water (according to MDG guidelines), or clean water is more than 30 minutes walking from home If they access water from: rainwater, tanker truck, cart with small tank/ drum, surface water, unprotected well, unprotected spring, then they do not have access to clean water'
                        )
                        poverty_indices.append(poverty_index)
                        water_deprived_decided = True
                except:
                    pass
            if not water_deprived_decided:
                answers = Answer.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                    question__question_code=WATER_SOURCE_QUESTION_CODE).filter(
                    text__in=['Rainwater', 'Tanker-truck', 'Cart with small tank/drum',
                              'Surface water (river, stream, dam, lake, pond, canal, irrigation channel)',
                              'Unprotected spring', 'Unprotected well', 'Other']).values_list('id', flat=True)
                mpi_query = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                    question__question_code=WATER_SOURCE_QUESTION_CODE,
                    section_response__survey_response_id=response.pk,
                    answer_id__in=answers
                ).first()
                if mpi_query:
                    mpi_score += 5.5
                    poverty_index = PGPovertyIndex(
                        primary_group_member_id=primary_group_member.pk, index_no=index,
                        index_name='Standard of Living (Water)',
                        index_description='The household does not have access to clean drinking water (according to MDG guidelines), or clean water is more than 30 minutes walking from home If they access water from: rainwater, tanker truck, cart with small tank/ drum, surface water, unprotected well, unprotected spring, then they do not have access to clean water'
                    )
                    poverty_indices.append(poverty_index)
            index += 1

            # For "The household has dirt, sand or dung floor" 5.5
            answers = Answer.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                question__question_code=FLOOR_TYPE_QUESTION_CODE).filter(
                text__in=['Earth/sand/semi pucca floor', 'Dung', 'Other']).values_list('id', flat=True)
            mpi_query = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                question__question_code=FLOOR_TYPE_QUESTION_CODE,
                section_response__survey_response_id=response.pk,
                answer_id__in=answers
            ).first()
            if mpi_query:
                mpi_score += 5.5
                poverty_index = PGPovertyIndex(
                    primary_group_member_id=primary_group_member.pk, index_no=index,
                    index_name='Standard of Living (Floor)',
                    index_description='The household has dirt, sand or dung floor'
                )
                poverty_indices.append(poverty_index)
            index += 1

            # For "The household cooks with dung, wood or charcoal" 5.5
            answers = Answer.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                question__question_code=FUEL_TYPE_QUESTION_CODE).filter(
                text__in=POOR_FUEL_ANSWERS).values_list('id', flat=True)
            mpi_query = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                question__question_code=FUEL_TYPE_QUESTION_CODE,
                section_response__survey_response_id=response.pk,
                answer_id__in=answers
            ).first()
            if mpi_query:
                mpi_score += 5.5
                poverty_index = PGPovertyIndex(
                    primary_group_member_id=primary_group_member.pk, index_no=index,
                    index_name='Standard of Living (Cooking Fuel)',
                    index_description='The household cooks with dung, wood or charcoal'
                )
                poverty_indices.append(poverty_index)
            index += 1

            # PG member is considered poor if they have 1 high resource value
            # and rich if they have more than 1 high resource and 1 car resource
            no_more_than_one = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                question__question_code=HH_RESOURCE_QUESTION_CODE,
                section_response__survey_response_id=response.pk,
                answer_text__in=HIGH_VALUE_RESOURCES
            ).count()
            if not no_more_than_one > 1:
                none_of_this = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                    question__question_code=HH_RESOURCE_QUESTION_CODE,
                    section_response__survey_response_id=response.pk,
                    answer_text__in=CAR_TRUCK_RESOURCE
                ).count()
                if not none_of_this:
                    mpi_score += 5.5
                    poverty_index = PGPovertyIndex(
                        primary_group_member_id=primary_group_member.pk, index_no=index,
                        index_name='Standard of Living (Assets)',
                        index_description='The household does not own more than one of: radio, TV, telephone, bike, motorbike or refrigerator, and does not'
                    )
                    poverty_indices.append(poverty_index)

            mpi_indicator = cls.objects.filter(primary_group_member_id=primary_group_member.pk).first()
            if not mpi_indicator:
                mpi_indicator = cls(primary_group_member_id=primary_group_member.pk)
            mpi_indicator.survey_response_id = response.pk
            mpi_indicator.mpi_score = mpi_score
            mpi_indicator.is_female_headed = is_female_headed
            mpi_indicator.is_male_headed = is_male_headed
            mpi_indicator.is_head_disabled = is_head_disabled
            mpi_indicator.is_minority = is_minority
            mpi_indicator.primary_group_member_id = primary_group_member.pk
            mpi_indicator.organization_id = organization_id
        return mpi_indicator, poverty_indices
