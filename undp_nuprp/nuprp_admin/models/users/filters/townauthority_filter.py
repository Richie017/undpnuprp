from django.db.models.query_utils import Q

from blackwidow.core.models.geography.geography import Geography
from undp_nuprp.nuprp_admin.models.infrastructure_units.household import Household
from undp_nuprp.reports.models.base.cache.question_response_cache import QuestionResponseCache
from undp_nuprp.survey.models.indicators.mpi_indicator import MPIIndicator
from undp_nuprp.survey.models.indicators.poverty_index import PovertyIndex
from undp_nuprp.survey.models.response.question_response import QuestionResponse
from undp_nuprp.survey.models.response.survey_response import SurveyResponse

__author__ = 'Ziaul Haque'


def get_filter_for_model(model_object, model):
    if model == Geography:
        return Q(
            **{'type': 'Country', 'pk': model_object.addresses.first().geography.parent.parent_id}) | Q(
            **{'type': 'Division', 'pk': model_object.addresses.first().geography.parent_id}) | Q(
            **{'type': 'Pourashava/City Corporation',
               'pk': model_object.addresses.first().geography.pk}) | Q(
            **{'type': 'Ward', 'parent_id': model_object.addresses.first().geography.pk})

    # Reporting Filters
    if model == QuestionResponse:
        return Q(**{'section_response__survey_response__address__geography__parent__parent__parent_id':
                        model_object.addresses.first().geography.pk})
    if model == QuestionResponseCache:
        return Q(**{'city': model_object.addresses.first().geography.pk})
    if model == MPIIndicator:
        return Q(**{
            'survey_response__address__geography__parent__parent__parent_id': model_object.addresses.first().geography.pk})
    if model == PovertyIndex:
        return Q(**{
            'household__surveyresponse__address__geography__parent__parent__parent_id': model_object.addresses.first().geography.pk})

    survey_response_related_models = (SurveyResponse, Household,)
    for obj in survey_response_related_models:
        if model == obj:
            return Q(**{'address__geography__parent__parent__parent_id': model_object.addresses.first().geography.pk})
    return None
