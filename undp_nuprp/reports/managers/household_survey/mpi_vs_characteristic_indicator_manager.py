"""
    Created by tareq on 3/13/17
"""

from django.db.models.aggregates import Avg

from blackwidow.engine.routers.database_router import BWDatabaseRouter

__author__ = 'Tareq'


def get_mpi_vs_characteristic_indicator_column_chart_data(wards=list(), from_time=None, to_time=None):
    from undp_nuprp.survey.models.indicators.mpi_indicator import MPIIndicator
    role_wise_query = MPIIndicator.get_role_based_queryset(queryset=MPIIndicator.objects.filter()).using(
        BWDatabaseRouter.get_read_database_name())
    mpi_domain = role_wise_query.filter(
        survey_response__survey_time__gte=from_time, survey_response__survey_time__lte=to_time
    )
    if wards:
        mpi_domain = mpi_domain.filter(survey_response__address__geography__parent__parent_id__in=wards)

    categories = ['Female headed households', 'Household head is disabled', 'Ethnic minorities', 'Other Households']

    avg_female = mpi_domain.filter(is_female_headed=True).aggregate(Avg('mpi_score'))['mpi_score__avg']
    avg_disabled = mpi_domain.filter(is_head_disabled=True).aggregate(Avg('mpi_score'))['mpi_score__avg']
    avg_minority = mpi_domain.filter(is_minority=True).aggregate(Avg('mpi_score'))['mpi_score__avg']
    avg_other = mpi_domain.filter(
        is_female_headed=False, is_head_disabled=False, is_minority=False).aggregate(Avg('mpi_score'))['mpi_score__avg']

    data = [
        {
            'name': 'Avg. MPI Score',
            'data': [
                avg_female if avg_female else 0,
                avg_disabled if avg_disabled else 0,
                avg_minority if avg_minority else 0,
                avg_other if avg_other else 0,
            ]
        }
    ]
    return data, categories
