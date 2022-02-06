"""
Created by tareq on 3/7/17
"""
from datetime import datetime

from crequest.middleware import CrequestMiddleware
from django import forms
from django.contrib.postgres.forms.ranges import DateRangeField
from django.db.models.aggregates import Min, Max
from django.urls.base import reverse
from django.utils.safestring import mark_safe

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.models.geography.geography import Geography
from blackwidow.core.models.geography.geography_level import GeographyLevel
from blackwidow.engine.decorators.utility import decorate, get_models_with_decorator
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.clock import Clock
from blackwidow.engine.extensions.color_code_generator import ColorCode
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from config.apps import INSTALLED_APPS
from config.model_json_cache import MODEL_JASON_URL
from undp_nuprp.reports.models.maps.survey_map_location import SurveyLocationReport
from undp_nuprp.reports.views.base.base_report import GenericReportView
from undp_nuprp.survey.models.response.survey_response import SurveyResponse

__author__ = 'Tareq'


@decorate(override_view(model=SurveyLocationReport, view=ViewActionEnum.Manage))
class SurveyMapLocationView(GenericReportView):
    def get_template_names(self):
        return ['reports/map_survey_location.html']

    def get_report_parameters(self, **kwargs):
        request = CrequestMiddleware.get_request()
        user = request.c_user
        user_role = user.role.name

        filter_roles = get_models_with_decorator(decorator_name='has_data_filter',
                                                 apps=INSTALLED_APPS, include_class=False)
        if user_role in filter_roles:
            json_suffix = '_' + str(user.pk)
        else:
            json_suffix = ''

        parameters = super(SurveyMapLocationView, self).get_report_parameters(**kwargs)
        division_level = GeographyLevel.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
            name__icontains='division').first()
        # starting_month = \
        #     SurveyResponse.objects.using(BWDatabaseRouter.get_read_database_name()).aggregate(Min('survey_time'))[
        #         'survey_time__min']
        # if starting_month:
        #     begin_time = datetime.fromtimestamp(starting_month / 1000).replace(day=1, hour=0, minute=0, second=0)
        #     date_range_initial = '%s - %s' % (
        #         begin_time.strftime('%d/%m/%Y'), datetime.now().strftime('%d/%m/%Y'))
        # else:
        import datetime as dt
        begin_time = datetime.now() - dt.timedelta(days=30)
        date_range_initial = '%s - %s' % (
            begin_time.strftime('%d/%m/%Y'), datetime.now().strftime('%d/%m/%Y'))

        parameters['G1'] = self.get_wrapped_parameters((
            {
                'name': 'division',
                'field': GenericModelChoiceField(
                    queryset=Geography.get_role_based_queryset(
                        queryset=Geography.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                            level_id=division_level.pk)),
                    label='Division',
                    empty_label=None,
                    required=False,
                    widget=forms.Select(
                        attrs={
                            'class': 'select2',
                            'width': '220',
                            'multiple': 'multiple',
                            'data-child': 'city_corporation',
                        }
                    )
                )
            },
        ))
        parameters['G2'] = self.get_wrapped_parameters((
            {
                'name': 'city_corporation',
                'field': forms.CharField(
                    label='City Corporation',
                    required=False,
                    widget=forms.TextInput(
                        attrs={
                            'width': '220',
                            'multiple': 'multiple',
                            'class': 'bw-select2',
                            'data-load-none': 'true',
                            'data-depends-on': 'division',
                            'data-depends-property': 'parent',
                            'data-js-url': '{0}{1}{2}.js'.format(MODEL_JASON_URL, Geography.__name__.lower(),
                                                                 json_suffix)
                        }
                    )
                )
            },
        ))
        parameters['G3'] = self.get_wrapped_parameters((
            {
                'name': 'ward',
                'field': forms.CharField(
                    label='Ward',
                    required=False,
                    widget=forms.TextInput(
                        attrs={
                            'width': '220',
                            'multiple': 'multiple',
                            'class': 'bw-select2',
                            'data-load-none': 'true',
                            'data-depends-on': 'city_corporation',
                            'data-depends-property': 'parent',
                            'data-js-url': '{0}{1}{2}.js'.format(MODEL_JASON_URL, Geography.__name__.lower(),
                                                                  json_suffix)
                        }
                    )
                )
            },
        ))
        parameters['G4'] = self.get_wrapped_parameters((
            {
                'name': 'date_range',
                'field': DateRangeField(
                    initial=date_range_initial,
                    widget=forms.TextInput(
                        attrs={
                            # 'data-initial-empty': "true",
                            'class': 'date-range-picker'
                        }
                    )
                )
            },
        ))
        return parameters

    def get_context_data(self, **kwargs):
        context = super(SurveyMapLocationView, self).get_context_data(**kwargs)
        context['title'] = "House Hold Survey Location"
        context['enable_map'] = True
        context['parameters'] = self.get_report_parameters(**kwargs)

        legend_colors = ColorCode.get_spaced_colors(1)
        context['legend_items'] = [{
            'id': 'survey',
            'color': '#' + legend_colors[0],
            'name': 'House Hold Survey Location'

        }]
        return context

    @staticmethod
    def str_to_list(data):
        """
        Simple function to  convert string to list
        :param data: 
        :return: a list(array) generated from data(str)
        """
        try:
            data_list = [int(x) for x in data.split(',')]
            return data_list
        except AttributeError:
            return data

    def get_json_response(self, content, **kwargs):
        # get all params from frontend
        division = self.extract_parameter('division')
        city_corporation = self.extract_parameter('city_corporation')
        ward = self.extract_parameter('ward')
        date_range = self.extract_parameter('date_range')

        # Convert str to list
        division = self.str_to_list(division)
        city_corporation = self.str_to_list(city_corporation)
        ward = self.str_to_list(ward)

        # convert JS datetime format(string) to milliseconds
        f_date, t_date = Clock.date_range_from_str(date_range)

        locations = list()
        # When date is empty or null
        if f_date is None:
            f_date = \
                SurveyResponse.objects.using(BWDatabaseRouter.get_read_database_name()).aggregate(Min('survey_time'))[
                    'survey_time__min']
        if t_date is None:
            t_date = SurveyResponse.objects.using(BWDatabaseRouter.get_read_database_name()).aggregate(
                max_time=Max('survey_time'))['max_time']

        role_wise_query = SurveyResponse.get_role_based_queryset(
            queryset=SurveyResponse.objects.using(BWDatabaseRouter.get_read_database_name()).all())
        queryset = role_wise_query.filter(
            location__isnull=False, survey_time__gte=f_date, survey_time__lte=t_date
        ).exclude(location__latitude__lte=0, location__longitude__lte=0)

        if ward:
            # If ward is selected
            queryset = queryset.filter(address__geography__parent__parent_id__in=ward)

        elif city_corporation:
            # If city corporation is selected
            queryset = queryset.filter(address__geography__parent__parent__parent_id__in=city_corporation)

        elif division:
            # If division is selected
            queryset = queryset.filter(address__geography__parent__parent__parent__parent_id__in=division)

        responses = queryset.values(
            'pk', 'respondent_unit__name', 'survey_time', 'location__latitude', 'location__longitude')

        for response in responses:
            locations.append({
                'type': 'survey',
                'name': response['respondent_unit__name'],
                'survey_time': mark_safe('<a class="inline-link" href="' + reverse(
                    SurveyResponse.get_route_name(ViewActionEnum.Details),
                    kwargs={'pk': response['pk']}) + '" target="_blank">' + datetime.fromtimestamp(
                    response['survey_time'] / 1000).strftime('%d/%m/%Y %I:%M %p') + '</a>'),
                'latitude': response['location__latitude'],
                'longitude': response['location__longitude']
            })

        data_dict = dict()
        data_dict['title'] = "House Hold Survey Location Map"
        data_dict['items'] = locations
        return super(SurveyMapLocationView, self).get_json_response(self.convert_context_to_json(data_dict), **kwargs)
