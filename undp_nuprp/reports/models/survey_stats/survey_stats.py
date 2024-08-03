import datetime

from django.db import models
from django.db.models import F

from blackwidow.core.models import Organization
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.utility import decorate, save_audit_log
from blackwidow.engine.extensions import bw_titleize
from blackwidow.engine.routers.database_router import BWDatabaseRouter

__author__ = 'Ziaul Haque'


@decorate(save_audit_log, expose_api('survey-statistics'), )
class SurveyStatistics(OrganizationDomainEntity):
    survey_name = models.CharField(max_length=255, null=True, default='')
    survey_key = models.CharField(max_length=255, null=True, default='')
    survey_user = models.ForeignKey('core.ConsoleUser', null=True, on_delete=models.SET_NULL)
    count_response_daily = models.IntegerField(default=0)
    count_response_monthly = models.IntegerField(default=0)
    count_response_all = models.IntegerField(default=0)

    class Meta:
        app_label = 'reports'

    @classmethod
    def get_serializer(cls):
        _OrganizationDomainEntitySerializer = OrganizationDomainEntity.get_serializer()

        class GeographySerializer(_OrganizationDomainEntitySerializer):
            class Meta:
                model = cls
                fields = 'id', 'survey_name', 'survey_key', 'survey_user', 'count_response_daily', \
                         'count_response_monthly', 'count_response_all', 'last_updated', 'last_updated'

        return GeographySerializer

    @classmethod
    def generate_survey_statistics(cls):
        from dynamic_survey.models import DynamicSurveyResponse
        from undp_nuprp.survey.models import SurveyResponse
        from undp_nuprp.approvals.models import CDCMonthlyReport, SCGMonthlyReport
        _today_start = datetime.datetime.now().replace(hour=0, minute=0, second=0).timestamp() * 1000
        _today_end = datetime.datetime.now().replace(hour=23, minute=59, second=59).timestamp() * 1000
        _this_month_start = datetime.datetime.now().replace(day=1, hour=0, minute=0).timestamp() * 1000
        _organization = Organization.objects.first()

        # survey statistics for Static Surveys (for example CDCMonthlyReport, SCGMonthlyReport)
        survey_models = [CDCMonthlyReport, SCGMonthlyReport]
        for _class in survey_models:
            _survey_name = bw_titleize(_class.__name__)
            _survey_key = _class.get_status_api_key()
            _survey_users = _class.objects.filter(created_by__isnull=False).values('created_by').distinct('created_by')

            for _survey_user in _survey_users:
                _user_id = _survey_user['created_by']

                _count_response_daily = _class.objects.filter(
                    date_created__gte=_today_start,
                    date_created__lte=_today_end,
                    created_by_id=_user_id, parent_id=F('id')
                ).count()
                _count_response_monthly = _class.objects.filter(
                    date_created__gte=_this_month_start,
                    created_by_id=_user_id, parent_id=F('id')
                ).count()
                _count_response_all = _class.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                    created_by_id=_user_id, parent_id=F('id')).count()

                if _count_response_daily + _count_response_monthly + _count_response_all > 0:
                    survey_statistics_object, created = SurveyStatistics.objects.using(
                        BWDatabaseRouter.get_write_database_name()).get_or_create(
                        survey_name=_survey_name, survey_key=_survey_key,
                        survey_user_id=_user_id, organization=_organization
                    )
                    survey_statistics_object.count_response_daily = _count_response_daily
                    survey_statistics_object.count_response_monthly = _count_response_monthly
                    survey_statistics_object.count_response_all = _count_response_all
                    survey_statistics_object.save()

                    if created:
                        print("Created Survey Statistics for user_id: %s, survey_name: %s" % (_user_id, _survey_name))
                    else:
                        print("Updated Survey Statistics for user_id: %s, survey_name: %s" % (_user_id, _survey_name))

        # survey statistics for Dynamic Surveys
        survey_models = [SurveyResponse, DynamicSurveyResponse]
        for _class in survey_models:
            _survey_key = _class.get_status_api_key()
            _surveys = _class.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                survey__isnull=False).values('survey__name').distinct('survey__name')
            _survey_users = _class.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                created_by__isnull=False).values('created_by').distinct('created_by')

            for _survey in _surveys:
                _survey_name = _survey['survey__name']
                for _survey_user in _survey_users:
                    _user_id = _survey_user['created_by']

                    _count_response_daily = _class.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                        date_created__gte=_today_start, date_created__lte=_today_end,
                        created_by_id=_user_id, survey__name=_survey_name
                    ).count()
                    _count_response_monthly = _class.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                        date_created__gte=_this_month_start,
                        created_by_id=_user_id,
                        survey__name=_survey_name
                    ).count()
                    _count_response_all = _class.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                        created_by_id=_user_id,
                        survey__name=_survey_name
                    ).count()

                    if _count_response_daily + _count_response_monthly + _count_response_all > 0:
                        survey_statistics_object, created = SurveyStatistics.objects.using(
                            BWDatabaseRouter.get_write_database_name()).get_or_create(
                            survey_name=_survey_name, survey_key=_survey_key, survey_user_id=_user_id,
                            organization=_organization
                        )
                        survey_statistics_object.count_response_daily = _count_response_daily
                        survey_statistics_object.count_response_monthly = _count_response_monthly
                        survey_statistics_object.count_response_all = _count_response_all
                        survey_statistics_object.save()
                        if created:
                            print(
                                "Created Survey Statistics for user_id: %s, survey_name: %s" % (_user_id, _survey_name))
                        else:
                            print(
                                "Updated Survey Statistics for user_id: %s, survey_name: %s" % (_user_id, _survey_name))
