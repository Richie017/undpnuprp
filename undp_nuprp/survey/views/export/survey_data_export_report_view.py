import datetime
from re import T
import string

from django import forms
from django.contrib.postgres.forms.ranges import DateRangeField
from django.db.models.aggregates import Max, Min

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.models.geography.geography import Geography
from blackwidow.core.models.geography.geography_level import GeographyLevel
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.clock import Clock
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from config.model_json_cache import MODEL_JASON_URL
from undp_nuprp.survey.models.export.survey_response_generated_file import SurveyResponseGeneratedFile
from undp_nuprp.reports.views.base.base_report import GenericReportView
from undp_nuprp.survey.models.entity.survey import Survey
from undp_nuprp.survey.models.export.survey_data_export_report import SurveyDataExportReport
from undp_nuprp.survey.models.response.survey_response import SurveyResponse

from django.http import HttpResponse

import random

__author__ = 'Ziaul Haque'


@decorate(override_view(model=SurveyDataExportReport, view=ViewActionEnum.Manage))
class SurveyDataExportReportView(GenericReportView):
    
    def get_template_names(self):
        return ['export/survey_data_export.html']

    def get_context_data(self, **kwargs):
        context = super(SurveyDataExportReportView, self).get_context_data(**kwargs)
        context['title'] = "Survey Data Export"
        return context

    def get_report_parameters(self, **kwargs):
        parameters = super(SurveyDataExportReportView, self).get_report_parameters(**kwargs)
        division_level = GeographyLevel.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
            name__icontains='division').first()

        parameters['G1'] = self.get_wrapped_parameters((
            {
                'name': 'survey',
                'field': GenericModelChoiceField(
                    queryset=Survey.objects.using(BWDatabaseRouter.get_read_database_name()).all(),
                    label='Survey',
                    empty_label=None,
                    required=False,
                    widget=forms.Select(
                        attrs={
                            'class': 'select2',
                            'width': '220',
                        }
                    )
                )
            },
        ))
        parameters['G2'] = self.get_wrapped_parameters((
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
                            'data-js-url': MODEL_JASON_URL + Geography.__name__.lower() + '.js'
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
                            'data-js-url': MODEL_JASON_URL + Geography.__name__.lower() + '.js'
                        }
                    )
                )
            },
        ))
        _todayDate = datetime.date.today()
        _first_date_of_month = _todayDate.replace(day=1).strftime('%d/%m/%Y')
        _yesterday_date = (_todayDate - datetime.timedelta(days=1)).strftime('%d/%m/%Y')
        _initial_date_range = str(_first_date_of_month + ' - ' + _yesterday_date)
        parameters['G4'] = self.get_wrapped_parameters((
            {
                'name': 'date_range',
                'field': DateRangeField(
                    initial=_initial_date_range,
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

    def process_parameters(self):
        date_range = self.extract_parameter('date_range')
        survey = self.extract_parameter('survey')
        division = self.extract_parameter('division')
        city_corporation = self.extract_parameter('city_corporation')
        ward = self.extract_parameter('ward')
        instant = self.extract_parameter('instant')

        division_ids = []
        city_ids = []
        ward_ids = []
        selected_wards = Geography.objects.none()

        if survey is not None:
            survey_id = int(survey)
        if division is not None:
            division_ids = [int(_id) for _id in division.split(',')]
            selected_wards = Geography.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                level__name__icontains='ward').filter(parent__parent_id__in=division_ids)
        if city_corporation is not None:
            city_ids = [int(_id) for _id in city_corporation.split(',')]
            selected_wards = Geography.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                level__name__icontains='ward').filter(parent_id__in=city_ids)
        if ward is not None:
            ward_ids = [int(_id) for _id in ward.split(',')]
            selected_wards = Geography.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                level__name__icontains='ward').filter(pk__in=ward_ids)

        f_date, t_date = Clock.date_range_from_str(date_range)
        if f_date is None:
            f_date = SurveyResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                survey_id=survey_id).aggregate(Min('survey_time'))['survey_time__min']
        if t_date is None:
            t_date = SurveyResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                survey_id=survey_id).aggregate(max_time=Max('survey_time'))['max_time']

        if selected_wards is not None:
            selected_wards = selected_wards.values_list('pk', flat=True)

        return survey_id, division_ids, city_ids, ward_ids, selected_wards, f_date, t_date, instant

    def get_json_response(self, content, **kwargs):
        survey_id, division_ids, city_ids, ward_ids, selected_wards, f_date, t_date, instant = self.process_parameters()
        if '0' in instant:
            report = SurveyDataExportReport. \
            build_report(divisions=division_ids, surveys=survey_id, cities=city_ids,
                         wards=ward_ids, domain=selected_wards, time_from=f_date, time_to=t_date)         
            return super(SurveyDataExportReportView, self).get_json_response(self.convert_context_to_json(report), **kwargs)
        else:
            ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))    
            SurveyResponseGeneratedFile.generate_excel(
                    time_from=f_date, time_to=t_date, survey_id=survey_id, year=None, month_name=None,
                    wards=selected_wards, filename=str("survey")+str(ran)+str(f_date)+"-"+str(t_date), mode='w'
                )
             
            return super(SurveyDataExportReportView, self).get_json_response(**kwargs)
          

        
