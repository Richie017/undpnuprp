"""
Created by tareq on 2/20/18
"""
import sys
from datetime import datetime

from django.db.models import Max

from blackwidow.core.models import Organization
from blackwidow.engine.extensions.date_age_converter import calculate_age
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.approvals.models import EligibleEducationDropOutGrantee, EligibleEducationEarlyMarriageGrantee, \
    GranteeGeneratedFile
from undp_nuprp.approvals.models.grantees.eligible_grantees.eligible_apprenticeship_grantee import \
    EligibleApprenticeshipGrantee
from undp_nuprp.approvals.models.grantees.eligible_grantees.eligible_business_grantee import EligibleBusinessGrantee
from undp_nuprp.approvals.models.grantees.eligible_grantees.eligible_education_grantee import EligibleEducationGrantee
from undp_nuprp.reports.config.constants.pg_survey_constants import PG_MEMBER_SURVEY_NAME, GENDER_QUESTION_CODE, \
    AGE_QUESTION_CODE, GRANT_FROM_ANY_ORGANIZATION_QUESTION_CODE, GRANT_FROM_NUPRP_QUESTION_CODE, \
    EMPLOYMENT_QUESTION_CODE, HH_NAME_QUESTION_CODE, NAME_QUESTION_CODE, ETHNICITY_QUESTION_CODE, \
    FORMAL_STUDENT_QUESTION_CODE, TRAINING_QUESTION_CODE, FAMILY_MEMBER_GENDER_QUESTION_CODE, \
    FAMILY_MEMBER_AGE_QUESTION_CODE, FAMILY_MEMBER_UPPR_GRANT_QUESTION_CODE, FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE, \
    FAMILY_MEMBER_TRAINING_QUESTION_CODE, FAMILY_MEMBER_FORMAL_STUDENT_QUESTION_CODE, \
    FAMILY_MEMBER_RELATION_QUESTION_CODE, FAMILY_MEMBER_APPRENTICESHIP_ALLOWED_RELATIONS, \
    FAMILY_MEMBER_NAME_QUESTION_CODE, FAMILY_MEMBER_EDUCATION_ALLOWED_RELATIONS, DISABILITY_COUNT_QUESTION_CODE, \
    GRANT_RECEIVED_FROM_ANY_ORGANIZATION_QUESTION_CODE, GRANT_RECEIVED_FROM_NUPRP_QUESTION_CODE, \
    FAMILY_MEMBER_UPPR_GRANT_TYPE_QUESTION_CODE, FAMILY_MEMBER_NUPRP_GRANT_TYPE_QUESTION_CODE, \
    FAMILY_MEMBER_EDUCATION_ALLOWED_TO_REDUCE_EARLY_MARRIAGE_RELATIONS, FAMILY_MEMBER_DISABILITY_QUESTION_CODE, \
    DISABLITY_QUESTION_CODE
from undp_nuprp.reports.config.constants.values import BATCH_SIZE
from undp_nuprp.survey.models.indicators.pg_mpi_indicator.mpi_indicator import PGMPIIndicator
from undp_nuprp.survey.models.response.question_response import QuestionResponse
from undp_nuprp.survey.models.response.survey_response import SurveyResponse

__author__ = 'Tareq'


class EligibleGranteeManager(object):

    @classmethod
    def generate_files(cls, last_run_time, handle_upto_time):
        print("Generating business grants file")
        # generating csv export file for EligibleBusinessGrantee list
        GranteeGeneratedFile.generate_complete_export_file(
            name=EligibleBusinessGrantee.get_export_file_name(),
            model=EligibleBusinessGrantee, last_run_time=last_run_time, handle_upto_time=handle_upto_time
        )

        print("Generating apprenticeshop grants file")
        # generating csv export file for EligibleApprenticeshipGrantee list
        GranteeGeneratedFile.generate_complete_export_file(
            name=EligibleApprenticeshipGrantee.get_export_file_name(),
            model=EligibleApprenticeshipGrantee, last_run_time=last_run_time, handle_upto_time=handle_upto_time
        )

        print("Generating EligibleEducationEarlyMarriageGrantee file")
        # generating csv export file for EligibleApprenticeshipGrantee list
        GranteeGeneratedFile.generate_complete_export_file(
            name=EligibleEducationEarlyMarriageGrantee.get_export_file_name(),
            model=EligibleEducationEarlyMarriageGrantee, last_run_time=last_run_time, handle_upto_time=handle_upto_time
        )

        print("Generating EligibleEducationDropOutGrantee grants file")
        # generating csv export file for EligibleApprenticeshipGrantee list
        GranteeGeneratedFile.generate_complete_export_file(
            name=EligibleEducationDropOutGrantee.get_export_file_name(),
            model=EligibleEducationDropOutGrantee, last_run_time=last_run_time, handle_upto_time=handle_upto_time
        )

    @classmethod
    def generate(cls, batch_count=None, batch_size=BATCH_SIZE):
        batch_size = 100
        max_survey_response_id = cls.get_max_handled_survey_response_id()
        max_handlable_survey_response_id = cls.get_max_handlable_survey_response_id()
        to_be_handled = SurveyResponse.objects.using(BWDatabaseRouter.get_read_database_name()).order_by('pk').filter(
            pk__gt=max_survey_response_id, pk__lte=max_handlable_survey_response_id,
            survey__name__icontains=PG_MEMBER_SURVEY_NAME).count()
        if batch_count is None:
            batch_count = sys.maxsize
        batch = 0
        total_handled = 0
        last_id = max_survey_response_id
        while batch < batch_count:
            batch += 1
            print(
                'Handling batch #{}: (starting from {}) {}/{}'.format(batch, last_id, total_handled + batch_size,
                                                                      to_be_handled))
            handled, last_id = cls.handle_eligible_grantee_selection(
                max_id=last_id, id_limit=max_handlable_survey_response_id, batch_size=batch_size)
            total_handled += handled
            if handled < batch_size:
                break

        print("Soft deleting deletable grantees...")
        cls.handle_pg_member_deletion()
        print("...deleted.")

    @classmethod
    def handle_eligible_grantee_selection(cls, max_id=0, id_limit=0, batch_size=BATCH_SIZE):
        candidate_responses = SurveyResponse.objects.using(BWDatabaseRouter.get_read_database_name()).order_by(
            'pk').filter(
            pk__gt=max_id, pk__lte=id_limit, survey__name__icontains=PG_MEMBER_SURVEY_NAME)[:batch_size]
        handled = 0
        for _sr in candidate_responses:
            max_id = _sr.pk
            cls.handle_eligible_grantee_selection_for_survey_response(survey_response=_sr)
            handled += 1

        return handled, max_id

    @classmethod
    def handle_pg_member_deletion(cls):
        deletable_business_grantees = EligibleBusinessGrantee.objects.filter(
            pg_member__is_deleted=True) | EligibleBusinessGrantee.objects.filter(pg_member__isnull=True)
        deletable_apprenticeship_grantees = EligibleApprenticeshipGrantee.objects.filter(
            pg_member__is_deleted=True) | EligibleApprenticeshipGrantee.objects.filter(pg_member__isnull=True)
        deletable_education_grantees = EligibleEducationGrantee.objects.filter(
            pg_member__is_deleted=True) | EligibleEducationGrantee.objects.filter(pg_member__isnull=True)

        try:
            deletable_business_grantees.delete()
            deletable_apprenticeship_grantees.delete()
            deletable_education_grantees.delete()
        except:
            pass

    @classmethod
    def handle_eligible_grantee_selection_for_survey_response(cls, survey_response, indvidually_edited=False):
        mpi_score = cls.get_respondent_mpi_score(survey_response)
        is_female_headed = cls.get_respondent_female_headed_status(survey_response)

        cls.handle_eligible_for_business_grant(survey_response, mpi_score, is_female_headed, indvidually_edited)
        cls.handle_eligible_for_apprenticeship_grant(survey_response, mpi_score, is_female_headed, indvidually_edited)
        cls.handle_eligible_for_drop_out_grant(survey_response, mpi_score, is_female_headed, indvidually_edited)
        cls.handle_eligible_for_early_marriage_grant(survey_response, mpi_score, is_female_headed, indvidually_edited)

    @classmethod
    def create_grantee(cls, grantee_class, survey_response, mpi_score, hh_name, grantee_name, age, gender, affiliation,
                       ethnicity, employment, other_grant_recipient, nuprp_grant_recipient, other_grant_type_recipient,
                       nuprp_grant_type_recipient, is_eligible, disability, is_female_headed, indvidually_edited=False):
        grantee = grantee_class(
            organization=Organization.get_organization_from_cache(), survey_response=survey_response,
            pg_member=survey_response.respondent_client, mpi_score=mpi_score, household_head_name=hh_name,
            grantee_name=grantee_name, age=age, gender=gender, affiliation=affiliation, ethnicity=ethnicity,
            employment=employment, other_grant_recipient=other_grant_recipient,
            nuprp_grant_recipient=nuprp_grant_recipient, other_grant_type_recipient=other_grant_type_recipient,
            nuprp_grant_type_recipient=nuprp_grant_type_recipient, is_eligible=is_eligible, disability=disability,
            is_female_headed=is_female_headed, date_created=survey_response.last_updated,
            indvidually_edited=indvidually_edited
        )
        try:
            grantee.address = survey_response.respondent_client.assigned_to.parent.address
        except:
            pass
        return grantee

    @classmethod
    def handle_eligible_for_business_grant(cls, survey_response, mpi_score, is_female_headed, indvidually_edited=False):
        grantees = list()

        # Clean existing data if exists
        EligibleBusinessGrantee.objects.filter(pg_member=survey_response.respondent_client).delete()

        necessary_responses = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
            section_response__survey_response_id=survey_response.pk, question__question_code__in=[
                GENDER_QUESTION_CODE, AGE_QUESTION_CODE, GRANT_FROM_ANY_ORGANIZATION_QUESTION_CODE,
                GRANT_RECEIVED_FROM_ANY_ORGANIZATION_QUESTION_CODE, GRANT_RECEIVED_FROM_NUPRP_QUESTION_CODE,
                GRANT_FROM_NUPRP_QUESTION_CODE, EMPLOYMENT_QUESTION_CODE, ETHNICITY_QUESTION_CODE,
                HH_NAME_QUESTION_CODE, NAME_QUESTION_CODE, DISABLITY_QUESTION_CODE
            ]).values('question__question_code', 'answer_text')
        ans_dict = dict()
        for r in necessary_responses:
            ans_dict[r['question__question_code']] = r['answer_text']

        pg_member_business = not (mpi_score < 20)

        # check if female
        if GENDER_QUESTION_CODE in ans_dict.keys() and ans_dict[GENDER_QUESTION_CODE].lower() != 'female':
            pg_member_business = False

        # check if age is between 25-50
        if AGE_QUESTION_CODE in ans_dict.keys() and not (25 <= cls.get_age_from_dob(ans_dict[AGE_QUESTION_CODE]) <= 50):
            pg_member_business = False

        if GRANT_RECEIVED_FROM_ANY_ORGANIZATION_QUESTION_CODE in ans_dict.keys() and ans_dict[
            GRANT_RECEIVED_FROM_ANY_ORGANIZATION_QUESTION_CODE].lower() == 'business grant':
            pg_member_business = False

        # check if receives NUPRP grants
        if GRANT_FROM_NUPRP_QUESTION_CODE in ans_dict.keys() and ans_dict[
            GRANT_FROM_NUPRP_QUESTION_CODE].lower() == 'yes':
            pg_member_business = False

        if EMPLOYMENT_QUESTION_CODE in ans_dict.keys() and ans_dict[
            EMPLOYMENT_QUESTION_CODE].lower().__contains__('skilled worker'):
            pg_member_business = False

        # check pg member is disabled or not
        disability = 'not disabled'
        for _question_code in DISABLITY_QUESTION_CODE:
            if _question_code in ans_dict.keys() and ans_dict[_question_code].lower() in ['A lot of difficulty',
                                                                                          'Cannot do at all']:
                disability = 'disabled'

        family_member_questions = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
            section_response__survey_response_id=survey_response.pk, question__question_code__in=[
                FAMILY_MEMBER_GENDER_QUESTION_CODE, FAMILY_MEMBER_AGE_QUESTION_CODE,
                FAMILY_MEMBER_UPPR_GRANT_QUESTION_CODE, FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE,
                FAMILY_MEMBER_UPPR_GRANT_TYPE_QUESTION_CODE, FAMILY_MEMBER_NUPRP_GRANT_TYPE_QUESTION_CODE,
                FAMILY_MEMBER_RELATION_QUESTION_CODE, FAMILY_MEMBER_NAME_QUESTION_CODE
            ]).values('question__question_code', 'answer_text', 'index')

        family_member_dict = dict()
        for fq in family_member_questions:
            if fq['index'] not in family_member_dict.keys():
                family_member_dict[fq['index']] = dict()
            member = family_member_dict[fq['index']]
            member[fq['question__question_code']] = fq['answer_text']

        for member in family_member_dict.values():
            # check if receives NUPRP grants
            if pg_member_business:
                if FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE in member.keys() and member[
                    FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE].lower() == 'yes':
                    pg_member_business = False

        grantees.append(cls.create_grantee(
            grantee_class=EligibleBusinessGrantee,
            survey_response=survey_response, mpi_score=mpi_score,
            hh_name=ans_dict[HH_NAME_QUESTION_CODE] if HH_NAME_QUESTION_CODE in ans_dict.keys() else '',
            age=cls.get_age_from_dob(
                ans_dict[AGE_QUESTION_CODE]) if AGE_QUESTION_CODE in ans_dict.keys() else '',
            affiliation='PG Member',
            ethnicity=ans_dict[ETHNICITY_QUESTION_CODE] if ETHNICITY_QUESTION_CODE in ans_dict.keys() else '',
            employment=ans_dict[
                EMPLOYMENT_QUESTION_CODE] if EMPLOYMENT_QUESTION_CODE in ans_dict.keys() else '',
            gender=ans_dict[GENDER_QUESTION_CODE] if GENDER_QUESTION_CODE in ans_dict.keys() else '',
            grantee_name=ans_dict[NAME_QUESTION_CODE] if NAME_QUESTION_CODE in ans_dict.keys() else '',
            nuprp_grant_recipient=ans_dict[
                GRANT_FROM_NUPRP_QUESTION_CODE] if GRANT_FROM_NUPRP_QUESTION_CODE in ans_dict.keys() else '',
            nuprp_grant_type_recipient=ans_dict[GRANT_RECEIVED_FROM_NUPRP_QUESTION_CODE] if
            GRANT_RECEIVED_FROM_NUPRP_QUESTION_CODE in ans_dict.keys() else '',
            other_grant_recipient=ans_dict[
                GRANT_FROM_ANY_ORGANIZATION_QUESTION_CODE] if GRANT_FROM_ANY_ORGANIZATION_QUESTION_CODE in ans_dict.keys() else '',
            other_grant_type_recipient=ans_dict[GRANT_RECEIVED_FROM_ANY_ORGANIZATION_QUESTION_CODE] if
            GRANT_RECEIVED_FROM_ANY_ORGANIZATION_QUESTION_CODE in ans_dict.keys() else '',
            is_eligible=pg_member_business,
            disability=disability,
            is_female_headed=is_female_headed, indvidually_edited=indvidually_edited
        ))

        for grantee in grantees:
            grantee.save(using=BWDatabaseRouter.get_write_database_name())

        return len(grantees)

    @classmethod
    def handle_eligible_for_apprenticeship_grant(cls, survey_response, mpi_score, is_female_headed,
                                                 indvidually_edited=False):
        grantees = list()

        # Clean existing data if exists
        EligibleApprenticeshipGrantee.objects.filter(pg_member=survey_response.respondent_client).delete()

        necessary_responses = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
            section_response__survey_response_id=survey_response.pk, question__question_code__in=[
                GENDER_QUESTION_CODE, AGE_QUESTION_CODE, GRANT_FROM_ANY_ORGANIZATION_QUESTION_CODE,
                GRANT_RECEIVED_FROM_ANY_ORGANIZATION_QUESTION_CODE, GRANT_RECEIVED_FROM_NUPRP_QUESTION_CODE,
                GRANT_FROM_NUPRP_QUESTION_CODE, EMPLOYMENT_QUESTION_CODE, FORMAL_STUDENT_QUESTION_CODE,
                TRAINING_QUESTION_CODE, ETHNICITY_QUESTION_CODE, HH_NAME_QUESTION_CODE, NAME_QUESTION_CODE,
                DISABLITY_QUESTION_CODE
            ]).values('question__question_code', 'answer_text')
        ans_dict = dict()
        for r in necessary_responses:
            ans_dict[r['question__question_code']] = r['answer_text']

        pg_member_apprentice = not (mpi_score < 20)
        check_family = not (mpi_score < 20)

        # check if age is between 18-35
        if not ans_dict[AGE_QUESTION_CODE] or not (18 <= cls.get_age_from_dob(ans_dict[AGE_QUESTION_CODE]) <= 35):
            pg_member_apprentice = False

        # check if receives other grants
        if pg_member_apprentice and (GRANT_RECEIVED_FROM_ANY_ORGANIZATION_QUESTION_CODE in ans_dict.keys() and ans_dict[
            GRANT_RECEIVED_FROM_ANY_ORGANIZATION_QUESTION_CODE].lower() == 'apprenticeship grant'):
            pg_member_apprentice = False
            check_family = False

        # check if receives NUPRP grants
        if pg_member_apprentice and GRANT_FROM_NUPRP_QUESTION_CODE in ans_dict.keys() and ans_dict[
            GRANT_FROM_NUPRP_QUESTION_CODE].lower() == 'yes':
            pg_member_apprentice = False
            check_family = False

        # check if student of formal education
        if pg_member_apprentice and FORMAL_STUDENT_QUESTION_CODE in ans_dict.keys() and ans_dict[
            FORMAL_STUDENT_QUESTION_CODE].lower() == 'yes':
            pg_member_apprentice = False

        # check if receiving training
        if pg_member_apprentice and TRAINING_QUESTION_CODE in ans_dict.keys() and ans_dict[
            TRAINING_QUESTION_CODE].lower() == 'yes':
            pg_member_apprentice = False

        # check if pg member in wage employment
        if pg_member_apprentice and EMPLOYMENT_QUESTION_CODE in ans_dict.keys() and ans_dict[
            EMPLOYMENT_QUESTION_CODE].lower().__contains__('skilled worker'):
            pg_member_apprentice = False

        # check pg member is disabled or not
        pg_member_disability = 'not disabled'
        for _question_code in DISABLITY_QUESTION_CODE:
            if _question_code in ans_dict.keys() and ans_dict[_question_code].lower() in ['A lot of difficulty',
                                                                                          'Cannot do at all']:
                pg_member_disability = 'disabled'

        family_member_questions = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
            section_response__survey_response_id=survey_response.pk, question__question_code__in=[
                FAMILY_MEMBER_GENDER_QUESTION_CODE, FAMILY_MEMBER_AGE_QUESTION_CODE,
                FAMILY_MEMBER_UPPR_GRANT_QUESTION_CODE, FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE,
                FAMILY_MEMBER_TRAINING_QUESTION_CODE, FAMILY_MEMBER_FORMAL_STUDENT_QUESTION_CODE,
                FAMILY_MEMBER_RELATION_QUESTION_CODE, FAMILY_MEMBER_NAME_QUESTION_CODE,
                FAMILY_MEMBER_UPPR_GRANT_TYPE_QUESTION_CODE, FAMILY_MEMBER_NUPRP_GRANT_TYPE_QUESTION_CODE,
                FAMILY_MEMBER_DISABILITY_QUESTION_CODE,
            ]).values('question__question_code', 'answer_text', 'index')

        family_member_dict = dict()
        for fq in family_member_questions:
            if fq['index'] not in family_member_dict.keys():
                family_member_dict[fq['index']] = dict()
            member = family_member_dict[fq['index']]
            member[fq['question__question_code']] = fq['answer_text']

        for member in family_member_dict.values():
            family_member_eligible = check_family
            # check if receives other grants
            if FAMILY_MEMBER_UPPR_GRANT_TYPE_QUESTION_CODE in member.keys() and member[
                FAMILY_MEMBER_UPPR_GRANT_TYPE_QUESTION_CODE].lower() == 'apprenticeship grant':
                pg_member_apprentice = False
                family_member_eligible = False
            # check if receives NUPRP grants
            if FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE in member.keys() and member[
                FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE].lower() == 'yes':
                pg_member_apprentice = False
                family_member_eligible = False
            # check if age is between 18-35
            if not FAMILY_MEMBER_AGE_QUESTION_CODE in member.keys() or not (
                    18 <= int(member[FAMILY_MEMBER_AGE_QUESTION_CODE]) <= 35):
                family_member_eligible = False
            # check if receives skill training
            if not FAMILY_MEMBER_TRAINING_QUESTION_CODE in member.keys() or member[
                FAMILY_MEMBER_TRAINING_QUESTION_CODE].lower() == 'yes':
                family_member_eligible = False
            # check if formal student
            if not FAMILY_MEMBER_FORMAL_STUDENT_QUESTION_CODE in member.keys() or member[
                FAMILY_MEMBER_FORMAL_STUDENT_QUESTION_CODE].lower() == 'yes':
                family_member_eligible = False

            # check family member disability status (disabled / not disabled)
            family_member_disability = 'not disabled'
            if FAMILY_MEMBER_DISABILITY_QUESTION_CODE in member.keys() and member[
                FAMILY_MEMBER_DISABILITY_QUESTION_CODE].lower() == 'disabled':
                family_member_disability = 'disabled'

            # check if correct relationship
            if not FAMILY_MEMBER_RELATION_QUESTION_CODE in member.keys() or not \
                    member[FAMILY_MEMBER_RELATION_QUESTION_CODE] in FAMILY_MEMBER_APPRENTICESHIP_ALLOWED_RELATIONS:
                continue  # We only record for allowed relations

            # Save member as grantee
            grantees.append(cls.create_grantee(
                grantee_class=EligibleApprenticeshipGrantee,
                survey_response=survey_response, mpi_score=mpi_score,
                hh_name=ans_dict[HH_NAME_QUESTION_CODE] if HH_NAME_QUESTION_CODE in ans_dict.keys() else '',
                age=member[FAMILY_MEMBER_AGE_QUESTION_CODE] if FAMILY_MEMBER_AGE_QUESTION_CODE in member.keys() else '',
                affiliation=member[
                    FAMILY_MEMBER_RELATION_QUESTION_CODE] if FAMILY_MEMBER_RELATION_QUESTION_CODE in member.keys() else '',
                ethnicity=ans_dict[ETHNICITY_QUESTION_CODE] if ETHNICITY_QUESTION_CODE in ans_dict.keys() else '',
                employment=ans_dict[EMPLOYMENT_QUESTION_CODE] if EMPLOYMENT_QUESTION_CODE in ans_dict.keys() else '',
                gender=member[
                    FAMILY_MEMBER_GENDER_QUESTION_CODE] if FAMILY_MEMBER_GENDER_QUESTION_CODE in member.keys() else '',
                grantee_name=member[
                    FAMILY_MEMBER_NAME_QUESTION_CODE] if FAMILY_MEMBER_NAME_QUESTION_CODE in member.keys() else '',
                nuprp_grant_recipient=member[
                    FAMILY_MEMBER_UPPR_GRANT_QUESTION_CODE] if FAMILY_MEMBER_UPPR_GRANT_QUESTION_CODE in member.keys() else '',
                other_grant_recipient=member[
                    FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE] if FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE in member.keys() else '',
                other_grant_type_recipient=ans_dict[FAMILY_MEMBER_UPPR_GRANT_TYPE_QUESTION_CODE] if
                FAMILY_MEMBER_UPPR_GRANT_TYPE_QUESTION_CODE in ans_dict.keys() else '',
                nuprp_grant_type_recipient=ans_dict[FAMILY_MEMBER_NUPRP_GRANT_TYPE_QUESTION_CODE] if
                FAMILY_MEMBER_NUPRP_GRANT_TYPE_QUESTION_CODE in ans_dict.keys() else '',
                is_eligible=family_member_eligible,
                disability=family_member_disability,
                is_female_headed=is_female_headed, indvidually_edited=indvidually_edited
            ))
        # Save PG member as grantee
        grantees.append(cls.create_grantee(
            grantee_class=EligibleApprenticeshipGrantee,
            survey_response=survey_response, mpi_score=mpi_score,
            hh_name=ans_dict[HH_NAME_QUESTION_CODE] if HH_NAME_QUESTION_CODE in ans_dict.keys() else '',
            age=cls.get_age_from_dob(ans_dict[AGE_QUESTION_CODE]) if AGE_QUESTION_CODE in ans_dict.keys() else '',
            affiliation='PG Member',
            ethnicity=ans_dict[ETHNICITY_QUESTION_CODE] if ETHNICITY_QUESTION_CODE in ans_dict.keys() else '',
            employment=ans_dict[EMPLOYMENT_QUESTION_CODE] if EMPLOYMENT_QUESTION_CODE in ans_dict.keys() else '',
            gender=ans_dict[GENDER_QUESTION_CODE] if GENDER_QUESTION_CODE in ans_dict.keys() else '',
            grantee_name=ans_dict[NAME_QUESTION_CODE] if NAME_QUESTION_CODE in ans_dict.keys() else '',
            nuprp_grant_recipient=ans_dict[
                GRANT_FROM_NUPRP_QUESTION_CODE] if GRANT_FROM_NUPRP_QUESTION_CODE in ans_dict.keys() else '',
            nuprp_grant_type_recipient=ans_dict[GRANT_RECEIVED_FROM_NUPRP_QUESTION_CODE] if
            GRANT_RECEIVED_FROM_NUPRP_QUESTION_CODE in ans_dict.keys() else '',
            other_grant_recipient=ans_dict[
                GRANT_FROM_ANY_ORGANIZATION_QUESTION_CODE] if GRANT_FROM_ANY_ORGANIZATION_QUESTION_CODE in ans_dict.keys() else '',
            other_grant_type_recipient=ans_dict[GRANT_RECEIVED_FROM_ANY_ORGANIZATION_QUESTION_CODE] if
            GRANT_RECEIVED_FROM_ANY_ORGANIZATION_QUESTION_CODE in ans_dict.keys() else '',
            is_eligible=pg_member_apprentice,
            disability=pg_member_disability,
            is_female_headed=is_female_headed
        ))

        for grantee in grantees:
            grantee.save(using=BWDatabaseRouter.get_write_database_name())

        return len(grantees)

    @classmethod
    def handle_eligible_for_drop_out_grant(cls, survey_response, mpi_score, is_female_headed, indvidually_edited=False):
        grantees = list()

        # Clean existing data if exists
        EligibleEducationDropOutGrantee.objects.filter(pg_member=survey_response.respondent_client).delete()

        necessary_responses = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
            section_response__survey_response_id=survey_response.pk, question__question_code__in=[
                GENDER_QUESTION_CODE, AGE_QUESTION_CODE, GRANT_FROM_ANY_ORGANIZATION_QUESTION_CODE,
                GRANT_FROM_NUPRP_QUESTION_CODE, EMPLOYMENT_QUESTION_CODE, FORMAL_STUDENT_QUESTION_CODE,
                TRAINING_QUESTION_CODE, ETHNICITY_QUESTION_CODE, HH_NAME_QUESTION_CODE, NAME_QUESTION_CODE,
                GRANT_RECEIVED_FROM_ANY_ORGANIZATION_QUESTION_CODE, GRANT_RECEIVED_FROM_NUPRP_QUESTION_CODE,
                DISABILITY_COUNT_QUESTION_CODE
            ]).values('question__question_code', 'answer_text')
        ans_dict = dict()
        for r in necessary_responses:
            ans_dict[r['question__question_code']] = r['answer_text']

        check_family = not (mpi_score < 20)
        if GRANT_FROM_NUPRP_QUESTION_CODE in ans_dict.keys() and ans_dict[
            GRANT_FROM_NUPRP_QUESTION_CODE].lower() == 'yes':
            check_family = False

        family_member_questions = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
            section_response__survey_response_id=survey_response.pk, question__question_code__in=[
                FAMILY_MEMBER_GENDER_QUESTION_CODE, FAMILY_MEMBER_AGE_QUESTION_CODE,
                FAMILY_MEMBER_UPPR_GRANT_QUESTION_CODE, FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE,
                FAMILY_MEMBER_TRAINING_QUESTION_CODE, FAMILY_MEMBER_FORMAL_STUDENT_QUESTION_CODE,
                FAMILY_MEMBER_NUPRP_GRANT_TYPE_QUESTION_CODE, FAMILY_MEMBER_UPPR_GRANT_TYPE_QUESTION_CODE,
                FAMILY_MEMBER_RELATION_QUESTION_CODE, FAMILY_MEMBER_NAME_QUESTION_CODE,
                FAMILY_MEMBER_DISABILITY_QUESTION_CODE
            ]).values('question__question_code', 'answer_text', 'index')

        student_count = 0
        disabled_count = int(ans_dict[DISABILITY_COUNT_QUESTION_CODE]) \
            if DISABILITY_COUNT_QUESTION_CODE in ans_dict.keys() else 0

        family_member_dict = dict()
        for fq in family_member_questions:
            if fq['index'] not in family_member_dict.keys():
                family_member_dict[fq['index']] = dict()
            member = family_member_dict[fq['index']]
            member[fq['question__question_code']] = fq['answer_text']

            if [fq['question__question_code']] == FAMILY_MEMBER_FORMAL_STUDENT_QUESTION_CODE and fq[
                'answer_text'].lower() == 'yes':
                student_count += 1

        for member in family_member_dict.values():
            family_member_eligible = check_family
            # check if receives NUPRP grants
            if FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE in member.keys() and member[
                FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE].lower() == 'yes':
                family_member_eligible = False
            # check if age is between 5-12
            if not FAMILY_MEMBER_AGE_QUESTION_CODE in member.keys() or not (
                    5 <= int(member[FAMILY_MEMBER_AGE_QUESTION_CODE]) <= 12):
                family_member_eligible = False

            # check family member disability status (disabled / not disabled)
            family_member_disability = 'not disabled'
            if FAMILY_MEMBER_DISABILITY_QUESTION_CODE in member.keys() and member[
                FAMILY_MEMBER_DISABILITY_QUESTION_CODE].lower() == 'disabled':
                family_member_disability = 'disabled'

            # check if correct relationship
            if not FAMILY_MEMBER_RELATION_QUESTION_CODE in member.keys() or not \
                    member[FAMILY_MEMBER_RELATION_QUESTION_CODE] in FAMILY_MEMBER_EDUCATION_ALLOWED_RELATIONS:
                continue  # We only record for allowed relations

            # Save member as grantee
            grantees.append(cls.create_grantee(
                grantee_class=EligibleEducationDropOutGrantee,
                survey_response=survey_response, mpi_score=mpi_score,
                hh_name=ans_dict[HH_NAME_QUESTION_CODE] if HH_NAME_QUESTION_CODE in ans_dict.keys() else '',
                age=member[FAMILY_MEMBER_AGE_QUESTION_CODE] if FAMILY_MEMBER_AGE_QUESTION_CODE in member.keys() else '',
                affiliation=member[
                    FAMILY_MEMBER_RELATION_QUESTION_CODE] if FAMILY_MEMBER_RELATION_QUESTION_CODE in member.keys() else '',
                ethnicity=ans_dict[ETHNICITY_QUESTION_CODE] if ETHNICITY_QUESTION_CODE in ans_dict.keys() else '',
                employment=ans_dict[EMPLOYMENT_QUESTION_CODE] if EMPLOYMENT_QUESTION_CODE in ans_dict.keys() else '',
                gender=member[
                    FAMILY_MEMBER_GENDER_QUESTION_CODE] if FAMILY_MEMBER_GENDER_QUESTION_CODE in member.keys() else '',
                grantee_name=member[
                    FAMILY_MEMBER_NAME_QUESTION_CODE] if FAMILY_MEMBER_NAME_QUESTION_CODE in member.keys() else '',
                nuprp_grant_recipient=member[
                    FAMILY_MEMBER_UPPR_GRANT_QUESTION_CODE] if FAMILY_MEMBER_UPPR_GRANT_QUESTION_CODE in member.keys() else '',
                other_grant_recipient=member[
                    FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE] if FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE in member.keys() else '',
                other_grant_type_recipient=ans_dict[FAMILY_MEMBER_UPPR_GRANT_TYPE_QUESTION_CODE] if
                FAMILY_MEMBER_UPPR_GRANT_TYPE_QUESTION_CODE in ans_dict.keys() else '',
                nuprp_grant_type_recipient=ans_dict[FAMILY_MEMBER_NUPRP_GRANT_TYPE_QUESTION_CODE] if
                FAMILY_MEMBER_NUPRP_GRANT_TYPE_QUESTION_CODE in ans_dict.keys() else '',
                is_eligible=family_member_eligible,
                disability=family_member_disability,
                is_female_headed=is_female_headed, indvidually_edited=indvidually_edited
            ))
        for grantee in grantees:
            grantee.school_going_count = student_count
            grantee.disabled_count = disabled_count
            grantee.save(using=BWDatabaseRouter.get_write_database_name())

        return len(grantees)

    @classmethod
    def handle_eligible_for_early_marriage_grant(cls, survey_response, mpi_score, is_female_headed,
                                                 indvidually_edited=False):
        grantees = list()

        # Clean existing data if exists
        EligibleEducationEarlyMarriageGrantee.objects.filter(pg_member=survey_response.respondent_client).delete()

        necessary_responses = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
            section_response__survey_response_id=survey_response.pk, question__question_code__in=[
                GENDER_QUESTION_CODE, AGE_QUESTION_CODE, GRANT_FROM_ANY_ORGANIZATION_QUESTION_CODE,
                GRANT_FROM_NUPRP_QUESTION_CODE, EMPLOYMENT_QUESTION_CODE, FORMAL_STUDENT_QUESTION_CODE,
                GRANT_RECEIVED_FROM_ANY_ORGANIZATION_QUESTION_CODE, GRANT_RECEIVED_FROM_NUPRP_QUESTION_CODE,
                TRAINING_QUESTION_CODE, ETHNICITY_QUESTION_CODE, HH_NAME_QUESTION_CODE, NAME_QUESTION_CODE,
                DISABILITY_COUNT_QUESTION_CODE
            ]).values('question__question_code', 'answer_text')
        ans_dict = dict()
        for r in necessary_responses:
            ans_dict[r['question__question_code']] = r['answer_text']

        check_family = not (mpi_score < 20)

        if GRANT_FROM_NUPRP_QUESTION_CODE in ans_dict.keys() and ans_dict[GRANT_FROM_NUPRP_QUESTION_CODE] == 'yes':
            check_family = False

        family_member_questions = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
            section_response__survey_response_id=survey_response.pk, question__question_code__in=[
                FAMILY_MEMBER_GENDER_QUESTION_CODE, FAMILY_MEMBER_AGE_QUESTION_CODE,
                FAMILY_MEMBER_UPPR_GRANT_QUESTION_CODE, FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE,
                FAMILY_MEMBER_TRAINING_QUESTION_CODE, FAMILY_MEMBER_FORMAL_STUDENT_QUESTION_CODE,
                FAMILY_MEMBER_UPPR_GRANT_TYPE_QUESTION_CODE, FAMILY_MEMBER_NUPRP_GRANT_TYPE_QUESTION_CODE,
                FAMILY_MEMBER_RELATION_QUESTION_CODE, FAMILY_MEMBER_NAME_QUESTION_CODE,
                FAMILY_MEMBER_DISABILITY_QUESTION_CODE
            ]).values('question__question_code', 'answer_text', 'index')

        student_count = 0
        disabled_count = int(ans_dict[DISABILITY_COUNT_QUESTION_CODE]) \
            if DISABILITY_COUNT_QUESTION_CODE in ans_dict.keys() else 0

        family_member_dict = dict()
        for fq in family_member_questions:
            if fq['index'] not in family_member_dict.keys():
                family_member_dict[fq['index']] = dict()
            member = family_member_dict[fq['index']]
            member[fq['question__question_code']] = fq['answer_text']

            if [fq['question__question_code']] == FAMILY_MEMBER_FORMAL_STUDENT_QUESTION_CODE and fq[
                'answer_text'].lower() == 'yes':
                student_count += 1

        for member in family_member_dict.values():
            family_member_eligible = check_family
            # check if receives NUPRP grants
            if FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE in member.keys() and member[
                FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE].lower() == 'yes':
                family_member_eligible = False
            # check if age is between 13-18
            if not FAMILY_MEMBER_AGE_QUESTION_CODE in member.keys() or not (
                    13 <= int(member[FAMILY_MEMBER_AGE_QUESTION_CODE]) <= 18):
                family_member_eligible = False
            # check if female
            if not FAMILY_MEMBER_GENDER_QUESTION_CODE in member.keys() or not \
                    member[FAMILY_MEMBER_GENDER_QUESTION_CODE] == 'Female':
                continue
            # check if correct relationship
            if not FAMILY_MEMBER_RELATION_QUESTION_CODE in member.keys() or not \
                    member[
                        FAMILY_MEMBER_RELATION_QUESTION_CODE] in FAMILY_MEMBER_EDUCATION_ALLOWED_TO_REDUCE_EARLY_MARRIAGE_RELATIONS:
                continue  # We only record for allowed relations (Daughter)

            # check family member disability status (disabled / not disabled)
            family_member_disability = 'not disabled'
            if FAMILY_MEMBER_DISABILITY_QUESTION_CODE in member.keys() and member[
                FAMILY_MEMBER_DISABILITY_QUESTION_CODE].lower() == 'disabled':
                family_member_disability = 'disabled'

            # Save member as grantee
            grantees.append(cls.create_grantee(
                grantee_class=EligibleEducationEarlyMarriageGrantee,
                survey_response=survey_response, mpi_score=mpi_score,
                hh_name=ans_dict[HH_NAME_QUESTION_CODE] if HH_NAME_QUESTION_CODE in ans_dict.keys() else '',
                age=member[FAMILY_MEMBER_AGE_QUESTION_CODE] if FAMILY_MEMBER_AGE_QUESTION_CODE in member.keys() else '',
                affiliation=member[
                    FAMILY_MEMBER_RELATION_QUESTION_CODE] if FAMILY_MEMBER_RELATION_QUESTION_CODE in member.keys() else '',
                ethnicity=ans_dict[ETHNICITY_QUESTION_CODE] if ETHNICITY_QUESTION_CODE in ans_dict.keys() else '',
                employment=ans_dict[EMPLOYMENT_QUESTION_CODE] if EMPLOYMENT_QUESTION_CODE in ans_dict.keys() else '',
                gender=member[
                    FAMILY_MEMBER_GENDER_QUESTION_CODE] if FAMILY_MEMBER_GENDER_QUESTION_CODE in member.keys() else '',
                grantee_name=member[
                    FAMILY_MEMBER_NAME_QUESTION_CODE] if FAMILY_MEMBER_NAME_QUESTION_CODE in member.keys() else '',
                nuprp_grant_recipient=member[
                    FAMILY_MEMBER_UPPR_GRANT_QUESTION_CODE] if FAMILY_MEMBER_UPPR_GRANT_QUESTION_CODE in member.keys() else '',
                other_grant_recipient=member[
                    FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE] if FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE in member.keys() else '',
                other_grant_type_recipient=ans_dict[FAMILY_MEMBER_UPPR_GRANT_TYPE_QUESTION_CODE] if
                FAMILY_MEMBER_UPPR_GRANT_TYPE_QUESTION_CODE in ans_dict.keys() else '',
                nuprp_grant_type_recipient=ans_dict[FAMILY_MEMBER_NUPRP_GRANT_TYPE_QUESTION_CODE] if
                FAMILY_MEMBER_NUPRP_GRANT_TYPE_QUESTION_CODE in ans_dict.keys() else '',
                is_eligible=family_member_eligible,
                disability=family_member_disability,
                is_female_headed=is_female_headed, indvidually_edited=indvidually_edited
            ))
        for grantee in grantees:
            grantee.school_going_count = student_count
            grantee.disabled_count = disabled_count
            grantee.save(using=BWDatabaseRouter.get_write_database_name())

        return len(grantees)

    @classmethod
    def get_respondent_mpi_score(cls, survey_response):
        mpi_indicator = PGMPIIndicator.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
            survey_response_id=survey_response.pk).first()
        if mpi_indicator is None:
            return 0  # not found
        return mpi_indicator.mpi_score

    @classmethod
    def get_respondent_female_headed_status(cls, survey_response):
        mpi_indicator = PGMPIIndicator.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
            survey_response_id=survey_response.pk).first()
        if mpi_indicator is None:
            return False  # not found
        return mpi_indicator.is_female_headed

    @classmethod
    def get_max_handled_survey_response_id(cls):
        max_business_id = EligibleBusinessGrantee.objects.filter(indvidually_edited=False).aggregate(
            Max('survey_response_id'))['survey_response_id__max']
        if max_business_id is None:
            max_business_id = 0
        max_app_id = EligibleApprenticeshipGrantee.objects.filter(indvidually_edited=False).aggregate(
            Max('survey_response_id'))['survey_response_id__max']
        if max_app_id is None:
            max_app_id = 0
        max_edu_id = EligibleEducationGrantee.objects.filter(indvidually_edited=False).aggregate(
            Max('survey_response_id'))['survey_response_id__max']
        if max_edu_id is None:
            max_edu_id = 0

        return max(max_business_id, max_app_id, max_edu_id)

    @classmethod
    def get_max_handlable_survey_response_id(cls):
        max_sr_mpi_id = PGMPIIndicator.objects.aggregate(Max('survey_response_id'))['survey_response_id__max']
        if max_sr_mpi_id is None:
            return 0
        return int(max_sr_mpi_id)

    @classmethod
    def get_age_from_dob(cls, dob):
        try:
            while True:
                try:
                    birth_date = datetime.strptime(dob, "%d-%b-%Y")
                    _age = int(calculate_age(birth_date))
                    break
                except:
                    _date, _month, _year = dob.split('-')
                    dob = str(
                        int(dob.split('-')[0]) - 1) + '-' + _month + '-' + _year  # decrease 1 day from current date
        except:
            current_year = int(datetime.now().year)
            birth_year = int(dob.split('-')[-1])
            _age = current_year - birth_year
        return _age
