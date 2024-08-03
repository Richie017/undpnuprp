from django.db.models.query_utils import Q

from blackwidow.core.models import Geography
from undp_nuprp.approvals.models import EligibleBusinessGrantee, EligibleApprenticeshipGrantee, \
    EligibleEducationDropOutGrantee, EligibleEducationEarlyMarriageGrantee, ApprovedSCGMonthlyReport, \
    PendingSCGMonthlyReport, PendingCDCMonthlyReport, ApprovedCDCMonthlyReport
from undp_nuprp.nuprp_admin.models import CDC, SavingsAndCreditGroup, PrimaryGroup, PrimaryGroupMember
from undp_nuprp.reports.models import SurveyStatistics

__author__ = 'Ziaul Haque'


def get_filter_for_model(model_object, model):
    if model == Geography:
        return Q(**{'type': 'Country',
                    'pk': model_object.addresses.first().geography.parent.parent.parent_id}) | Q(
            **{'type': 'Division',
               'pk': model_object.addresses.first().geography.parent.parent_id}) | Q(
            **{'type': 'Pourashava/City Corporation',
               'pk': model_object.addresses.first().geography.parent_id}) | Q(
            **{'type': 'Ward', 'parent__pk': model_object.addresses.first().geography.parent_id})
    if model == PrimaryGroupMember:
        return Q(**{'assigned_to__parent__pk__in': model_object.infrastructureunit_set.values_list('pk',
                                                                                                   flat=True)})
    if model == PrimaryGroupMember:
        return Q(**{'assigned_to__parent__pk__in': model_object.infrastructureunit_set.values_list('pk',
                                                                                                   flat=True)})
    if model == PrimaryGroup:
        return Q(**{'parent__pk__in': model_object.infrastructureunit_set.values_list('pk', flat=True)})
    if model == CDC:
        return Q(**{'pk__in': model_object.infrastructureunit_set.values_list('pk', flat=True)})
    if model == SavingsAndCreditGroup:
        return Q(**{
            'primary_group__parent__pk__in': model_object.infrastructureunit_set.values_list('pk',
                                                                                             flat=True)})
    if model == EligibleBusinessGrantee:
        return Q(**{
            'pg_member__assigned_to__parent__pk__in': model_object.infrastructureunit_set.values_list(
                'pk', flat=True)})
    if model == EligibleApprenticeshipGrantee:
        return Q(**{
            'pg_member__assigned_to__parent__pk__in': model_object.infrastructureunit_set.values_list(
                'pk', flat=True)})
    if model == EligibleEducationDropOutGrantee:
        return Q(**{
            'pg_member__assigned_to__parent__pk__in': model_object.infrastructureunit_set.values_list(
                'pk', flat=True)})
    if model == EligibleEducationEarlyMarriageGrantee:
        return Q(**{
            'pg_member__assigned_to__parent__pk__in': model_object.infrastructureunit_set.values_list(
                'pk', flat=True)})
    if model == PendingSCGMonthlyReport:
        return Q(
            **{'scg__primary_group__parent__pk__in': model_object.infrastructureunit_set.values_list(
                'pk', flat=True)})
    if model == ApprovedSCGMonthlyReport:
        return Q(
            **{'scg__primary_group__parent__pk__in': model_object.infrastructureunit_set.values_list(
                'pk', flat=True)})
    if model == PendingCDCMonthlyReport:
        return Q(
            **{'scg__primary_group__parent__pk__in': model_object.infrastructureunit_set.values_list(
                'pk', flat=True)})
    if model == ApprovedCDCMonthlyReport:
        return Q(
            **{'scg__primary_group__parent__pk__in': model_object.infrastructureunit_set.values_list(
                'pk', flat=True)})

    # survey statistics
    if model == SurveyStatistics:
        Q(**{'survey_user_id': model_object.id})

    return None
