from datetime import date, datetime, timedelta

from django import forms

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from dynamic_survey.models import DynamicSurveyResponseGeneratedFile
from dynamic_survey.models.design.dynamic_survey import DynamicSurvey
from undp_nuprp.reports.views.base.base_report import GenericReportView
from undp_nuprp.survey.models.export.dynamic_survey_data_exporter import DynamicSurveyDataExporter

__author__ = 'Ziaul Haque'


@decorate(override_view(model=DynamicSurveyDataExporter, view=ViewActionEnum.Manage))
class DynamicSurveyDataExporterView(GenericReportView):
    def get_template_names(self):
        return ['export/dynamic_survey_data_export.html']

    def get_context_data(self, **kwargs):
        context = super(DynamicSurveyDataExporterView, self).get_context_data(**kwargs)
        context['title'] = "Dynamic Survey Export File Generator"
        return context

    def get_report_parameters(self, **kwargs):
        parameters = super(DynamicSurveyDataExporterView, self).get_report_parameters(**kwargs)

        today = date.today().replace(day=1)
        year_choices = tuple()
        month_choices = tuple(
            [(today.replace(month=i).strftime('%B'), today.replace(month=i).strftime('%B'))
             for i in range(1, 13)])
        for y in range(2000, 2100):
            year_choices += ((y, str(y)),)

        parameters['G1'] = self.get_wrapped_parameters((
            {
                'name': 'survey',
                'field': GenericModelChoiceField(
                    queryset=DynamicSurvey.objects.using(BWDatabaseRouter.get_read_database_name()).all(),
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
                'name': 'year',
                'field': forms.ChoiceField(
                    label='Year',
                    required=False,
                    choices=year_choices,
                    widget=forms.Select(
                        attrs={
                            'width': '220',
                            'class': 'select2',
                        }
                    )
                )
            },
        ))

        parameters['G3'] = self.get_wrapped_parameters((
            {
                'name': 'month',
                'field': forms.ChoiceField(
                    label='Month',
                    required=False,
                    choices=month_choices,
                    widget=forms.Select(
                        attrs={
                            'width': '220',
                            'class': 'select2',
                        }
                    )
                )
            },
        ))
        return parameters

    def process_parameters(self):
        survey = self.extract_parameter('survey')
        year = self.extract_parameter('year')
        month = self.extract_parameter('month')

        survey_id = None
        if survey is not None:
            survey_id = int(survey)

        return survey_id, int(year), month

    def get_json_response(self, content, **kwargs):
        survey_id, year, month = self.process_parameters()
        print(survey_id, year, month)

        if survey_id:
            given_date = datetime.strptime("{},{}".format(month, year), "%B,%Y")
            month = given_date.month + 1
            if month > 12:
                month = 1
                year += 1
            given_date = given_date.replace(year=year, month=month)
            given_date -= timedelta(seconds=1)

            month_start = given_date.replace(day=1, hour=0, minute=0, second=0).timestamp() * 1000
            year = int(given_date.strftime("%Y"))  # Clock.millisecond_to_date_str(time_to, _format="%Y")
            month = int(given_date.strftime("%m"))  # Clock.millisecond_to_date_str(time_to, _format="%B")

            existing_file = DynamicSurveyResponseGeneratedFile.objects.filter(
                year=year, survey_id=survey_id, month=month,
            ).order_by('-date_created').first()
            if existing_file:
                DynamicSurveyResponseGeneratedFile.objects.filter(
                    pk=existing_file.pk
                ).update(last_updated=month_start)

            DynamicSurveyResponseGeneratedFile.generate_export_files_in_given_time(
                generation_time=given_date,
                survey_id=survey_id,
                mode='w',
                last_generated_timestamp=month_start
            )
            print("export file generated...")
    
        return super(DynamicSurveyDataExporterView, self).get_json_response(**kwargs)
