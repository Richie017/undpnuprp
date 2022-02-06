import datetime

from django.db import transaction
from django.db.models import F

from blackwidow.core.models.users.user import ConsoleUser
from undp_nuprp.approvals.models import SEFEducationDropoutGrantee
from undp_nuprp.approvals.models.grantees.eligible_grantees.eligible_apprenticeship_grantee import \
    EligibleApprenticeshipGrantee
from undp_nuprp.approvals.models.grantees.eligible_grantees.eligible_business_grantee import EligibleBusinessGrantee
from undp_nuprp.approvals.models.grantees.eligible_grantees.eligible_education_drop_out_grantee import \
    EligibleEducationDropOutGrantee
from undp_nuprp.approvals.models.grantees.eligible_grantees.eligible_education_early_marriage_grantee import \
    EligibleEducationEarlyMarriageGrantee
from undp_nuprp.approvals.models.sef_grant_disbursement.sef_grant_disbursement import SEFGrantDisbursement
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_apprenticeship_grantee import \
    SEFApprenticeshipGrantee
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_business_grantee import SEFBusinessGrantee
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_education_early_marriage_grantee import \
    SEFEducationChildMarriageGrantee
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_nutrition_grantee import SEFNutritionGrantee
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group_member import PrimaryGroupMember
from undp_nuprp.reports.models.cache.pg_member_info_cache import PGMemberInfoCache
from undp_nuprp.survey.models.indicators.mpi_indicator import MPIIndicator
from undp_nuprp.survey.models.indicators.pg_mpi_indicator.mpi_indicator import PGMPIIndicator
from undp_nuprp.survey.models.indicators.pg_mpi_indicator.poverty_index import PGPovertyIndex
from undp_nuprp.survey.models.response.question_response import QuestionResponse
from undp_nuprp.survey.models.response.section_response import SectionResponse
from undp_nuprp.survey.models.response.survey_response import SurveyResponse

__author__ = 'Shuvro'


class PGSurveyDeletionManager(object):
    @classmethod
    def delete_pg_survey(cls, survey_response_id, user):
        _question_responses = QuestionResponse.objects.filter(section_response__survey_response_id=survey_response_id)

        _count = 0
        for _qr in _question_responses:
            _qr.soft_delete(force_delete=True, user=user)
            _count += 1
        print('Total {} question responses has deleted'.format(_count))

        _count = 0
        _section_responses = SectionResponse.objects.filter(survey_response_id=survey_response_id)
        for _sr in _section_responses:
            _sr.soft_delete(force_delete=True, user=user)
            _count += 1

        print('Total {} section response data has deleted'.format(_count))

        _sr = SurveyResponse.objects.filter(id=survey_response_id).first()
        _sr.soft_delete(force_delete=True, user=user)
        print('Survey ID:{} has deleted successfully'.format(survey_response_id))

    @classmethod
    def delete_pg_survey_and_its_reference(cls, city=None, from_time=None, to_time=None):
        if not city:
            raise Exception('City is mandatory')
        if not from_time:
            raise Exception('From date is mandatory')
        if not to_time:
            raise Exception('To date is mandatory')

        _user = ConsoleUser.objects.first()

        with transaction.atomic():
            _survey_responses = SurveyResponse.objects.filter(
                respondent_client__assigned_to__parent__address__geography__parent__name=city,
                survey_time__gte=from_time, survey_time__lte=to_time)
            response_ids = list(_survey_responses.values_list('pk', flat=True))

            _pgm_queryset = PrimaryGroupMember.objects.filter(surveyresponse__in=response_ids)
            _pgm_ids = list(_pgm_queryset.values_list('pk', flat=True))

            # SEF grant disbursement deletion
            SEFGrantDisbursement.objects.filter(pg_member_id__in=_pgm_ids).update(
                deleted_level=F('deleted_level') + 1,
                is_deleted=True,
                is_active=False,
                last_updated=int(datetime.datetime.now().timestamp() * 1000)
            )

            # SEF grantee deletion
            SEFBusinessGrantee.objects.filter(pg_member_id__in=_pgm_ids).update(
                deleted_level=F('deleted_level') + 1,
                is_deleted=True,
                is_active=False,
                last_updated=int(datetime.datetime.now().timestamp() * 1000)
            )

            SEFApprenticeshipGrantee.objects.filter(pg_member_id__in=_pgm_ids).update(
                deleted_level=F('deleted_level') + 1,
                is_deleted=True,
                is_active=False,
                last_updated=int(datetime.datetime.now().timestamp() * 1000)
            )

            SEFEducationChildMarriageGrantee.objects.filter(pg_member_id__in=_pgm_ids).update(
                deleted_level=F('deleted_level') + 1,
                is_deleted=True,
                is_active=False,
                last_updated=int(datetime.datetime.now().timestamp() * 1000)
            )

            SEFEducationDropoutGrantee.objects.filter(pg_member_id__in=_pgm_ids).update(
                deleted_level=F('deleted_level') + 1,
                is_deleted=True,
                is_active=False,
                last_updated=int(datetime.datetime.now().timestamp() * 1000)
            )

            SEFNutritionGrantee.objects.filter(pg_member_id__in=_pgm_ids).update(
                deleted_level=F('deleted_level') + 1,
                is_deleted=True,
                is_active=False,
                last_updated=int(datetime.datetime.now().timestamp() * 1000)
            )

            # Eligible grantee deletion
            EligibleBusinessGrantee.objects.filter(survey_response_id__in=response_ids).update(
                deleted_level=F('deleted_level') + 1,
                is_deleted=True,
                is_active=False,
                last_updated=int(datetime.datetime.now().timestamp() * 1000)
            )

            EligibleApprenticeshipGrantee.objects.filter(survey_response_id__in=response_ids).update(
                deleted_level=F('deleted_level') + 1,
                is_deleted=True,
                is_active=False,
                last_updated=int(datetime.datetime.now().timestamp() * 1000)
            )

            EligibleEducationEarlyMarriageGrantee.objects.filter(survey_response_id__in=response_ids).update(
                deleted_level=F('deleted_level') + 1,
                is_deleted=True,
                is_active=False,
                last_updated=int(datetime.datetime.now().timestamp() * 1000)
            )

            EligibleEducationDropOutGrantee.objects.filter(survey_response_id__in=response_ids).update(
                deleted_level=F('deleted_level') + 1,
                is_deleted=True,
                is_active=False,
                last_updated=int(datetime.datetime.now().timestamp() * 1000)
            )

            # Delete MPI score
            print('Deleting MPIIndicator')
            MPIIndicator.objects.filter(survey_response_id__in=response_ids).update(
                deleted_level=F('deleted_level') + 1,
                is_deleted=True,
                is_active=False,
                last_updated=int(datetime.datetime.now().timestamp() * 1000)
            )

            # Delete PGMPIIndicator
            print('Deleting PGMPIIndicator')
            PGMPIIndicator.objects.filter(survey_response_id__in=response_ids).update(
                deleted_level=F('deleted_level') + 1,
                is_deleted=True,
                is_active=False,
                last_updated=int(datetime.datetime.now().timestamp() * 1000)
            )

            # Delete PG member cache info
            print('Deleting PGMemberInfoCache')
            PGMemberInfoCache.objects.filter(from_time__gte=from_time, to_time__lte=to_time,
                                             city__name=city).update(
                deleted_level=F('deleted_level') + 1,
                is_deleted=True,
                is_active=False,
                last_updated=int(datetime.datetime.now().timestamp() * 1000)
            )

            print('Deleting PGPovertyIndex')
            PGPovertyIndex.objects.filter(primary_group_member_id__in=_pgm_ids).update(
                deleted_level=F('deleted_level') + 1,
                is_deleted=True,
                is_active=False,
                last_updated=int(datetime.datetime.now().timestamp() * 1000)
            )

            _survey_responses.update(respondent_client=None)
            PrimaryGroupMember.objects.filter(id__in=_pgm_ids).update(
                deleted_level=F('deleted_level') + 1,
                is_deleted=True,
                is_active=False,
                last_updated=int(datetime.datetime.now().timestamp() * 1000)
            )

            _survey_responses = SurveyResponse.objects.filter(id__in=response_ids)
            for _sr in _survey_responses:
                # Delete survey and its responses
                _id = _sr.id
                print('Deleting survey response ID: {}'.format(_id))
                cls.delete_pg_survey(survey_response_id=_sr.id, user=_user)
                print('Successfully deleted')

            return _survey_responses.count()
