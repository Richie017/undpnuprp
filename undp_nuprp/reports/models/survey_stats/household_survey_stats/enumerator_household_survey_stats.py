"""
Created by tareq on 4/25/17
"""
from django.db.models.aggregates import Count
from django.urls.base import reverse
from django.utils.safestring import mark_safe

from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models.users.enumerator import Enumerator
from undp_nuprp.reports.config.constants.pg_survey_constants import PG_MEMBER_SURVEY_NAME
from undp_nuprp.reports.models.base.base import Report
from undp_nuprp.survey.models.response.survey_response import SurveyResponse

__author__ = 'Tareq'


@decorate(is_object_context,
          route(route='enumerator-stats', group='Enumerator\'s Detail', group_order=2,
                module=ModuleEnum.Administration, display_name="Enumerator Survey Stats", item_order=2))
class EnumeratorHouseholdSurveyStats(Report):
    class Meta:
        proxy = True

    @classmethod
    def build_report(cls, surveys=None, cities=None, wards=None, domain=None, time_from=None, time_to=None,
                     styled=False):

        headers = ['City/Town', ]
        orders = ['respondent_client__assigned_to__parent__address__geography__parent__name', ]
        values = ['respondent_client__assigned_to__parent__address__geography__parent__name', ]
        fixed_columns = 1
        total_row_prefix = ['Total']

        if wards:
            headers += ['Ward']
            orders += ['respondent_client__assigned_to__parent__address__geography__name']
            values += ['respondent_client__assigned_to__parent__address__geography__name']
            fixed_columns += 1
            total_row_prefix += ['']

        queryset = SurveyResponse.objects.using(
            BWDatabaseRouter.get_read_database_name()
        ).filter(survey__name=PG_MEMBER_SURVEY_NAME)
        if surveys:
            queryset = queryset.filter(survey_id__in=surveys)
        if domain:
            queryset = queryset.filter(respondent_client__assigned_to__parent__address__geography_id__in=domain)
        if time_from:
            queryset = queryset.filter(survey_time__gte=time_from)
        if time_to:
            queryset = queryset.filter(survey_time__lte=time_to)

        values += ['created_by_id', 'created_by__name', 'created_by__user__username', 'created_by__code']

        queryset = queryset.order_by(*tuple(orders)).values(*tuple(values)).annotate(count=Count('pk', distinct=True))

        headers += ['Enumerator', 'Mobile No', 'Number of survey']

        if styled:
            headers = tuple(headers)

        report = list()
        report.append(headers)

        total_enums = 0
        total_survey = 0
        total_city = 0
        total_ward = 0

        old_city = None
        old_ward = None
        enum_list = list()
        for survey in queryset:
            city = survey['respondent_client__assigned_to__parent__address__geography__parent__name']
            row = [city]
            if old_city != city:
                total_city += 1
                old_city = city
            if wards:
                ward = '%s - %s' % (city, survey['respondent_client__assigned_to__parent__address__geography__name'])
                row += [ward]
                if old_ward != ward:
                    total_ward += 1
                    old_ward = ward
            enumerator = '%s: %s' % (survey['created_by__code'], survey['created_by__name'])
            if not styled:
                enumerator = mark_safe('<a href="' + reverse(Enumerator.get_route_name(ViewActionEnum.Details), kwargs={
                    'pk': survey['created_by_id']}) + '" target="_blank">' + enumerator + '</a>')
            row += [enumerator]
            row += [survey['created_by__user__username'], str(survey['count'])]

            if not enumerator in enum_list:
                total_enums += 1
                enum_list.append(enumerator)
            total_survey += survey['count']

            if styled:
                row = tuple(row)
            report.append(row)

        total_row = ['%d City/Town(s)' % total_city]
        if len(total_row_prefix) > 1:
            total_row += ['%d Ward(s)' % total_ward]
        total_row += [('%d Enumerator(s)' % total_enums), ('%d Mobile No(s)' % total_enums), str(total_survey)]
        if styled:
            total_row = tuple(total_row)
        report.append(total_row)

        return report, 0  # fixed_columns
