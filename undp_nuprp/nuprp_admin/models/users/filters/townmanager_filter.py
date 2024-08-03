from django.db.models.query_utils import Q

from blackwidow.core.models.geography.geography import Geography
from undp_nuprp.approvals.models import EligibleBusinessGrantee, EligibleApprenticeshipGrantee, \
    EligibleEducationDropOutGrantee, EligibleEducationEarlyMarriageGrantee, PendingSCGMonthlyReport, \
    ApprovedSCGMonthlyReport, PendingCDCMonthlyReport, ApprovedCDCMonthlyReport
from undp_nuprp.nuprp_admin.models import DuplcateIdAlert, SavingsAndCreditReportAlert
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc import CDC
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc_cluster import CDCCluster
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group import PrimaryGroup
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group_member import PrimaryGroupMember
from undp_nuprp.nuprp_admin.models.infrastructure_units.savings_and_credit_group import SavingsAndCreditGroup
from undp_nuprp.nuprp_admin.models.users.town_manager import TownManager
from undp_nuprp.survey.models.response.survey_response import SurveyResponse

__author__ = 'Ziaul Haque'


def get_filter_for_model(model_object, model, database='default'):
    if model == Geography:
        return Q(
            **{'type': 'Country', 'pk': model_object.addresses.first().geography.parent.parent_id}) | Q(
            **{'type': 'Division', 'pk': model_object.addresses.first().geography.parent_id}) | Q(
            **{'type': 'Pourashava/City Corporation',
               'pk': model_object.addresses.first().geography.id}) | Q(
            **{'type': 'Ward', 'parent_id': model_object.addresses.first().geography.id}) | Q(
            **{'type': 'Mahalla', 'parent__parent_id': model_object.addresses.first().geography.id})
    if model == CDCCluster:
        return Q(**{'address__geography_id': model_object.addresses.first().geography.id})
    if model == CDC:
        return Q(**{'address__geography__parent_id': model_object.addresses.first().geography.id})
    if model == PrimaryGroup:
        return Q(
            **{'parent__address__geography__parent_id': model_object.addresses.first().geography.id})
    if model == PrimaryGroupMember:
        return Q(**{'assigned_to__parent__address__geography__parent_id': model_object.addresses.first().geography.id})
    if model == SavingsAndCreditGroup:
        return Q(
            **{'primary_group__parent__address__geography__parent_id': model_object.addresses.first().geography.id})
    if model == SurveyResponse:
        return Q(**{
            'respondent_client__assigned_to__parent__address__geography__parent_id': model_object.addresses.first().geography.id})
    if model == EligibleBusinessGrantee:
        return Q(**{
            'pg_member__assigned_to__parent__address__geography__parent__pk': model_object.addresses.first().geography.id})
    if model == EligibleApprenticeshipGrantee:
        return Q(**{
            'pg_member__assigned_to__parent__address__geography__parent__pk': model_object.addresses.first().geography.id})
    if model == EligibleEducationDropOutGrantee:
        return Q(**{
            'pg_member__assigned_to__parent__address__geography__parent__pk': model_object.addresses.first().geography.id})
    if model == EligibleEducationEarlyMarriageGrantee:
        return Q(**{
            'pg_member__assigned_to__parent__address__geography__parent__pk': model_object.addresses.first().geography.id})
    if model == PendingSCGMonthlyReport:
        return Q(**{
            'scg__primary_group__parent__address__geography__parent__pk': model_object.addresses.first().geography.id})
    if model == ApprovedSCGMonthlyReport:
        return Q(**{
            'scg__primary_group__parent__address__geography__parent__pk': model_object.addresses.first().geography.id})
    if model == PendingCDCMonthlyReport:
        return Q(**{'cdc__address__geography__parent__pk': model_object.addresses.first().geography.id})
    if model == ApprovedCDCMonthlyReport:
        return Q(**{'cdc__address__geography__parent__pk': model_object.addresses.first().geography.id})
    if model == TownManager:
        return Q(**{'pk': model_object.id})

    # Alerts
    if model == DuplcateIdAlert:
        return Q(**{'created_by__addresses__geography__parent__pk': model_object.addresses.first().geography.id})
    if model == SavingsAndCreditReportAlert:
        return Q(**{'cdc_reports__cdc__address__geography__parent__pk': model_object.addresses.first().geography.id}) | \
               Q(**{'scg_reports__scg__address__geography__pk': model_object.addresses.first().geography.id})
    return None
