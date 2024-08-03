"""
Created by tareq on 4/5/18
"""
from datetime import datetime

from django.db.models import Count

from blackwidow.engine.constants.cache_constants import ONE_MONTH_TIMEOUT
from blackwidow.engine.managers.cachemanager import CacheManager
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.config.constants.pg_survey_constants import PG_MEMBER_SURVEY_NAME
from undp_nuprp.survey.models import SurveyResponse

__author__ = 'Tareq'


class EnumeratorSurveyStatisticsManager(object):
    @classmethod
    def cleanup_deleted_pg_member_survey(cls):
        deletable_surveys = SurveyResponse.objects.filter(
            respondent_client__is_deleted=True) | SurveyResponse.objects.filter(
            survey__name=PG_MEMBER_SURVEY_NAME, respondent_client__isnull=True)

        current_timestamp = datetime.now().timestamp() * 1000
        deletable_surveys.update(is_deleted=True, deleted_level=1, last_updated=current_timestamp)

    @classmethod
    def update_enumerator_survey_statistics_cache(cls):
        survey_response_queryset = SurveyResponse.objects.using(BWDatabaseRouter.get_read_database_name()).values(
            'created_by_id', 'survey_id', 'survey__name').annotate(count=Count('pk'))
        enumerator_stats_dict = dict()
        for srq in survey_response_queryset:
            enum_id = srq['created_by_id']
            if enum_id not in enumerator_stats_dict.keys():
                enumerator_stats_dict[enum_id] = dict()
            survey_dict = enumerator_stats_dict[enum_id]

            if srq['survey_id'] not in survey_dict.keys():
                survey_dict[srq['survey_id']] = {
                    'survey_name': srq['survey__name'],
                    'count': 0
                }
            survey_entry = survey_dict[srq['survey_id']]
            survey_entry['count'] += srq['count']

        for key, value in enumerator_stats_dict.items():
            cache_key = SurveyResponse.get_cache_prefix() + str(key)
            CacheManager.set_cache_element_by_key(key=cache_key, value=value, timeout=ONE_MONTH_TIMEOUT)
