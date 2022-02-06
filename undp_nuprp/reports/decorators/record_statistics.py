import datetime
from threading import Thread

from django.db.models import F

from blackwidow.core.models import Organization
from blackwidow.engine.extensions import bw_titleize

__author__ = "Ziaul Haque"


def record_statistics(original_class):
    from undp_nuprp.reports.models.survey_stats.survey_stats import SurveyStatistics

    def update_survey_statistics(_class, instance):
        """
        update survey response statistics user specific
        """
        _survey_key = _class.get_status_api_key()
        _survey_user = instance.created_by
        _organization = Organization.objects.first()

        _today_start = datetime.datetime.now().replace(hour=0, minute=0, second=0).timestamp() * 1000
        _today_end = datetime.datetime.now().replace(hour=23, minute=59, second=59).timestamp() * 1000
        _this_month_start = datetime.datetime.now().replace(day=1, hour=0, minute=0).timestamp() * 1000

        if _class.__name__ == 'SurveyResponse' or _class.__name__ == 'DynamicSurveyResponse':
            _surveys = _class.objects.filter(
                created_by=_survey_user, survey__isnull=False
            ).values('survey__name').distinct('survey__name')
            for _survey in _surveys:
                _survey_name = _survey['survey__name']
                _count_response_daily = _class.objects.filter(
                    date_created__gte=_today_start, date_created__lte=_today_end,
                    created_by=_survey_user, survey__name=_survey_name
                ).count()
                _count_response_monthly = _class.objects.filter(
                    date_created__gte=_this_month_start,
                    created_by=_survey_user,
                    survey__name=_survey_name
                ).count()
                _count_response_all = _class.objects.filter(
                    created_by=_survey_user,
                    survey__name=_survey_name
                ).count()

                if _count_response_daily + _count_response_monthly + _count_response_all > 0:
                    survey_statistics_object, created = SurveyStatistics.objects.get_or_create(
                        survey_name=_survey_name, survey_key=_survey_key, survey_user=_survey_user,
                        organization=_organization
                    )
                    survey_statistics_object.count_response_daily = _count_response_daily
                    survey_statistics_object.count_response_monthly = _count_response_monthly
                    survey_statistics_object.count_response_all = _count_response_all
                    survey_statistics_object.save()
        else:
            # if survey response comes from static surveys (like SCG Monthly Report, CDC Monthly Report)
            _survey_name = bw_titleize(_class.__name__)
            _count_response_daily = _class.objects.filter(
                date_created__gte=_today_start,
                date_created__lte=_today_end,
                created_by=_survey_user,
                parent_id=F('id')
            ).count()
            _count_response_monthly = _class.objects.filter(
                date_created__gte=_this_month_start,
                created_by=_survey_user,
                parent_id=F('id')
            ).count()
            _count_response_all = _class.objects.filter(created_by=_survey_user, parent_id=F('id')).count()

            if _count_response_daily + _count_response_monthly + _count_response_all > 0:
                survey_statistics_object, created = SurveyStatistics.objects.get_or_create(
                    survey_name=_survey_name, survey_key=_survey_key,
                    survey_user=_survey_user, organization=_organization
                )
                survey_statistics_object.count_response_daily = _count_response_daily
                survey_statistics_object.count_response_monthly = _count_response_monthly
                survey_statistics_object.count_response_all = _count_response_all
                survey_statistics_object.save()

    def save(self, *args, **kwargs):
        save._original(self, *args, **kwargs)
        # perform survey response statistics in thread
        update_survey_statistics(self._meta.model, self)
        # process = Thread(target=update_survey_statistics, args=(self._meta.model, self))
        # process.start()

    save._original = original_class.save
    original_class.save = save

    return original_class
