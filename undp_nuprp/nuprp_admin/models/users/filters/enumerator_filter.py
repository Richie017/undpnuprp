from django.db.models.query_utils import Q

from blackwidow.core.models.geography.geography import Geography
from undp_nuprp.nuprp_admin.models import CDC, PrimaryGroup, PrimaryGroupMember, Enumerator
from undp_nuprp.nuprp_admin.models.infrastructure_units.savings_and_credit_group import SavingsAndCreditGroup
from undp_nuprp.reports.models import SurveyStatistics

__author__ = 'Tareq'


def get_filter_for_model(model_object, model):
    if model == Geography:
        return Q(**{'type': 'Country',
                    'pk': model_object.addresses.first().geography.parent.parent.parent_id}) | Q(
            **{'type': 'Division',
               'pk': model_object.addresses.first().geography.parent.parent_id}) | Q(
            **{'type': 'Pourashava/City Corporation',
               'pk': model_object.addresses.first().geography.parent_id}) | Q(
            **{'type': 'Ward', 'parent_id': model_object.addresses.first().geography.parent_id})

    if model == CDC:
        return Q(
            **{'address__geography__parent__pk': model_object.addresses.first().geography.parent_id})

    if model == PrimaryGroup:
        return Q(**{'parent__address__geography__parent__pk': model_object.addresses.first().geography.parent_id})

    if model == SavingsAndCreditGroup:
        return Q(**{'address__geography_id': model_object.addresses.first().geography.parent_id})

    if model == PrimaryGroupMember:
        return Q(**{
            'assigned_to__parent__address__geography__parent__pk': model_object.addresses.first().geography.parent_id})

    if model == SurveyStatistics:
        return Q(**{'survey_user_id': model_object.id})

    if model == Enumerator:
        return Q(**{'pk': model_object.id})
    return None
