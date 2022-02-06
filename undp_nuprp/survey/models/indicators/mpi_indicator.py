"""
    Created by tareq on 3/13/17
"""
import sys

from django.db import models

from blackwidow.core.models.organizations.organization import Organization
from undp_nuprp.reports.config.constants.values import BATCH_SIZE
from undp_nuprp.reports.models.base.cache.cache_base import CacheBase
from undp_nuprp.survey.models.entity.answer import Answer
from undp_nuprp.survey.models.indicators.poverty_index import PovertyIndex
from undp_nuprp.survey.models.response.question_response import QuestionResponse
from undp_nuprp.survey.models.response.survey_response import SurveyResponse

__author__ = 'Tareq'


class MPIIndicator(CacheBase):
    survey_response = models.ForeignKey('survey.SurveyResponse')
    household = models.ForeignKey('nuprp_admin.Household', null=True)
    is_female_headed = models.BooleanField(default=False)
    is_head_disabled = models.BooleanField(default=False)
    is_minority = models.BooleanField(default=False)
    mpi_score = models.FloatField(default=0)

    @classmethod
    def generate(cls, batch_count=None, batch_size=BATCH_SIZE):
        to_be_handled = SurveyResponse.objects.filter(mpiindicator__isnull=True).count()
        if batch_count is None:
            batch_count = sys.maxsize
        batch = 0
        total_handled = 0
        while batch < batch_count:
            batch += 1
            print('Handling batch #{}: {}/{}'.format(batch, total_handled + batch_size, to_be_handled))
            handled = cls.handle_mpi_calculation(batch_size=batch_size)
            total_handled += handled
            if handled < batch_size:
                break

    @classmethod
    def handle_mpi_calculation(cls, batch_size=BATCH_SIZE):
        candidate_responses = SurveyResponse.objects.filter(mpiindicator__isnull=True)[:batch_size]

        creatable_mpi_list = list()

        organization_id = Organization.objects.first().pk

        for response in candidate_responses:
            mpi_score = 0
            index = 1
            household = response.respondent_unit

            # is female headed
            is_female_headed = False
            female_response = QuestionResponse.objects.filter(
                section_response__survey_response_id=response.pk, question__question_code='1.5',
                answer_text__iexact='Female').first()
            if female_response:
                is_female_headed = True

            # is disabled
            is_head_disabled = False
            disabled_response = QuestionResponse.objects.filter(
                section_response__survey_response_id=response.pk,
                question__question_code__in=['3.1', '3.2', '3.3', '3.4', '3.5', '3.6'],
                answer_text__in=['Cannot do at all', 'A lot of difficulty']).first()
            if disabled_response:
                is_head_disabled = True

            # is minority
            is_minority = False
            bengali_response = QuestionResponse.objects.filter(
                section_response__survey_response_id=response.pk, question__question_code='1.7',
                answer_text__iexact='Bengali').first()
            if bengali_response:
                is_minority = True

            poverty_indices = list()

            # For "Has any member of the household completed 5 years of schooling or more?" -> "No" 16.7
            mpi_query = QuestionResponse.objects.filter(
                question__question_code='4.1', section_response__survey_response_id=response).last()
            if mpi_query and mpi_query.answer_text.lower() == 'no':
                mpi_score += 16.7
                poverty_index = PovertyIndex(
                    household_id=household.pk, index_no=index, index_name='Education (Years of Schooling)',
                    index_description='No household member has completed five years of schooling'
                )
                poverty_indices.append(poverty_index)
            index += 1

            # For "Any school-aged child is attending school in years 1 to 8" -> "No" 16.7
            mpi_query = QuestionResponse.objects.filter(
                question__question_code='4.1.2', section_response__survey_response_id=response).last()
            if mpi_query and mpi_query.answer_text.lower() == 'no':
                mpi_score += 16.7
                poverty_index = PovertyIndex(
                    household_id=household.pk, index_no=index, index_name='Education (Child School Attendance)',
                    index_description='Any school-aged child is not attending school in years 1 to 8'
                )
                poverty_indices.append(poverty_index)
            index += 1

            # For "Has the adult head of the family ever given birth to a son or daughter who was born alive but later died, between 0-5 years" -> "Yes" 16.7
            mpi_query = QuestionResponse.objects.filter(
                question__question_code='4.9.1', section_response__survey_response_id=response).last()
            if mpi_query and mpi_query.answer_text.lower() == 'yes':
                mpi_score += 16.7
                poverty_index = PovertyIndex(
                    household_id=household.pk, index_no=index, index_name='Health (Mortality)',
                    index_description='Any child has died in the family'
                )
                poverty_indices.append(poverty_index)
            index += 1

            # For "Is the household head of the family disabled" -> "Yes" 16.7
            mpi_query = QuestionResponse.objects.filter(
                question__question_code='2.6', section_response__survey_response_id=response).last()
            if mpi_query and mpi_query.answer_text.lower() == 'yes':
                mpi_score += 16.7
                poverty_index = PovertyIndex(
                    household_id=household.pk, index_no=index, index_name='Disability',
                    index_description='Household head is disabled'
                )
                poverty_indices.append(poverty_index)
            index += 1

            # For "The household has no electricity" 5.5
            mpi_query = QuestionResponse.objects.filter(
                question__question_code='4.8', section_response__survey_response_id=response,
                answer_text__iexact='Electricity').last()
            if not mpi_query:
                mpi_score += 5.5
                poverty_index = PovertyIndex(
                    household_id=household.pk, index_no=index, index_name='Standard of Living (Electricity)',
                    index_description='The household has no electricity'
                )
                poverty_indices.append(poverty_index)
            index += 1

            # For "Sanitation not improved" 5.5
            mpi_query = QuestionResponse.objects.filter(
                question__question_code='4.4', section_response__survey_response_id=response,
                answer_text__iexact='yes').last()
            if mpi_query:
                mpi_score += 5.5
                poverty_index = PovertyIndex(
                    household_id=household.pk, index_no=index, index_name='Standard of Living (Sanitation)',
                    index_description='The household\'s sanitation facility is not improved (according to MDG guidelines), or it is improved but shared with other households. If the HH has the following sanitation facility then it is not improved: pit latrine without slab/ open pit, bucket, hanging toilet, no facilities or bush/ field'
                )
                poverty_indices.append(poverty_index)
            else:
                answers = Answer.objects.filter(question__question_code='4.3').filter(text__in=[
                    'Pit latrine without slab / open pit', 'Bucket', 'Hanging toilet/hanging latrine',
                    'No facilities or bush or field', 'Other'
                ]).values_list('id', flat=True)
                mpi_query = QuestionResponse.objects.filter(
                    question__question_code='4.3', section_response__survey_response_id=response,
                    answer_id__in=answers).first()
                if mpi_query:
                    mpi_score += 5.5
                    poverty_index = PovertyIndex(
                        household_id=household.pk, index_no=index, index_name='Standard of Living (Sanitation)',
                        index_description='The household\'s sanitation facility is not improved (according to MDG guidelines), or it is improved but shared with other households. If the HH has the following sanitation facility then it is not improved: pit latrine without slab/ open pit, bucket, hanging toilet, no facilities or bush/ field'
                    )
                    poverty_indices.append(poverty_index)
            index += 1

            # For "No access of drinking water" 5.5
            mpi_query = QuestionResponse.objects.filter(
                question__question_code='4.6.1', section_response__survey_response_id=response).first()
            if mpi_query:
                try:
                    minutes = float(mpi_query.answer_text)
                    if minutes > 30:
                        mpi_score += 5.5
                        poverty_index = PovertyIndex(
                            household_id=household.pk, index_no=index, index_name='Standard of Living (Water)',
                            index_description='The household does not have access to clean drinking water (according to MDG guidelines), or clean water is more than 30 minutes walking from home If they access water from: rainwater, tanker truck, cart with small tank/ drum, surface water, unprotected well, unprotected spring, then they do not have access to clean water'
                        )
                        poverty_indices.append(poverty_index)
                except:
                    pass
            else:
                answers = Answer.objects.filter(question__question_code='4.6').filter(
                    text__in=['Rainwater', 'Tanker-truck', 'Cart with small tank/drum',
                              'Surface water (river, stream, dam, lake, pond, canal, irrigation channel)',
                              'Unprotected spring', 'Unprotected well', 'Other']).values_list('id', flat=True)
                mpi_query = QuestionResponse.objects.filter(
                    question__question_code='4.6', section_response__survey_response_id=response,
                    answer_id__in=answers
                ).first()
                if mpi_query:
                    mpi_score += 5.5
                    poverty_index = PovertyIndex(
                        household_id=household.pk, index_no=index, index_name='Standard of Living (Water)',
                        index_description='The household does not have access to clean drinking water (according to MDG guidelines), or clean water is more than 30 minutes walking from home If they access water from: rainwater, tanker truck, cart with small tank/ drum, surface water, unprotected well, unprotected spring, then they do not have access to clean water'
                    )
                    poverty_indices.append(poverty_index)
            index += 1

            # For "The household has dirt, sand or dung floor" 5.5
            answers = Answer.objects.filter(question__question_code='4.2').filter(
                text__in=['Earth/sand', 'Dung', 'Other']).values_list('id', flat=True)
            mpi_query = QuestionResponse.objects.filter(
                question__question_code='4.2', section_response__survey_response_id=response,
                answer_id__in=answers
            ).first()
            if mpi_query:
                mpi_score += 5.5
                poverty_index = PovertyIndex(
                    household_id=household.pk, index_no=index, index_name='Standard of Living (Floor)',
                    index_description='The household has dirt, sand or dung floor'
                )
                poverty_indices.append(poverty_index)
            index += 1

            # For "The household cooks with dung, wood or charcoal" 5.5
            answers = Answer.objects.filter(question__question_code='4.5').filter(
                text__in=['Wood', 'Charcoal', 'Animal dung', 'Other']).values_list('id', flat=True)
            mpi_query = QuestionResponse.objects.filter(
                question__question_code='4.5', section_response__survey_response_id=response,
                answer_id__in=answers
            ).first()
            if mpi_query:
                mpi_score += 5.5
                poverty_index = PovertyIndex(
                    household_id=household.pk, index_no=index, index_name='Standard of Living (Cooking Fuel)',
                    index_description='The household cooks with dung, wood or charcoal'
                )
                poverty_indices.append(poverty_index)
            index += 1

            # For "Bad standard of living" 5.5
            no_more_than_one = QuestionResponse.objects.filter(
                question__question_code='4.8', section_response__survey_response_id=response,
                answer_text__in=['Radio', 'Refrigerator', 'Television', 'Land phone', 'Mobile Phone', 'Bicycle',
                                 'Motorbike/Scooter']
            ).count()
            if not no_more_than_one > 1:
                none_of_this = QuestionResponse.objects.filter(
                    question__question_code='4.8', section_response__survey_response_id=response,
                    answer_text__in=['Car', 'Truck']
                ).count()
                if not none_of_this:
                    mpi_score += 5.5
                    poverty_index = PovertyIndex(
                        household_id=household.pk, index_no=index, index_name='Standard of Living (Assets)',
                        index_description='The household does not own more than one of: radio, TV, telephone, bike, motorbike or refrigerator, and does not'
                    )
                    poverty_indices.append(poverty_index)

            mpi_indicator = cls(survey_response_id=response.pk, mpi_score=mpi_score,
                                is_female_headed=is_female_headed,
                                is_head_disabled=is_head_disabled, is_minority=is_minority,
                                household_id=household.pk,
                                organization_id=organization_id)
            creatable_mpi_list.append(mpi_indicator)

        PovertyIndex.objects.bulk_create(poverty_indices)
        MPIIndicator.objects.bulk_create(creatable_mpi_list)
        return candidate_responses.count()
