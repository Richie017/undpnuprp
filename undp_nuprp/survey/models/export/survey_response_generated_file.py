"""
Created by tareq on 4/27/17
"""
from curses import echo
import os
from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.db.models.aggregates import Min
from django.urls.base import reverse
from django.utils.safestring import mark_safe
from savReaderWriter.savWriter import SavWriter

from blackwidow.core.models.contracts.base import DomainEntity
from blackwidow.core.models.file.exportfileobject import ExportFileObject
from blackwidow.core.models.file.imagefileobject import ImageFileObject
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.bw_titleize import bw_compress_name
from blackwidow.engine.extensions.clock import Clock
from blackwidow.engine.extensions.console_debug import bw_debug
from blackwidow.engine.file_handlers.aws_file_writer import AWSFileWriter
from blackwidow.engine.file_handlers.file_path_handler import FilePathHandler
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from config.aws_s3_config import MEDIA_DIRECTORY
from config.database import MC_WRITE_DATABAE_NAME
from undp_nuprp.nuprp_admin.utils.enums.question_type_enum import QuestionTypeEnum
from undp_nuprp.reports.config.constants.pg_survey_constants import FAMILY_MEMBER_LIMIT, MPI_HH_RESOURCE_LIST
from undp_nuprp.survey.models.entity.question import Question
from undp_nuprp.survey.models.entity.survey import Survey
from undp_nuprp.survey.models.indicators.mpi_indicator import MPIIndicator
from undp_nuprp.survey.models.indicators.pg_mpi_indicator.mpi_indicator import PGMPIIndicator
from undp_nuprp.survey.models.response.question_response import QuestionResponse
from undp_nuprp.survey.models.response.survey_response import SurveyResponse

import csv

from django.http import StreamingHttpResponse

EXPORT_FILE_ROOT = settings.EXPORT_FILE_ROOT
S3_STATIC_ENABLED = settings.S3_STATIC_ENABLED

__author__ = 'Tareq, Ziaul Haque'


@decorate(is_object_context,
          route(route='survey-response-export', group='Download Data', module=ModuleEnum.Administration,
                display_name='Monthly Survey Data Export', item_order=100, group_order=4))
class SurveyResponseGeneratedFile(DomainEntity):
    survey = models.ForeignKey('survey.Survey', null=True, on_delete=models.SET_NULL)
    month = models.IntegerField(default=1)
    year = models.IntegerField(default=2017)
    format = models.CharField(max_length=32, blank=True)
    file = models.ForeignKey('core.FileObject', null=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'survey'

  

    @classmethod
    def default_order_by(cls):
        return ['-year', '-month']

    @property
    def render_code(self):
        return self.code

    @property
    def render_month(self):
        year = self.year if self.year else 'N/A'
        if not self.month:
            return 'All Surveys'
        month = self.month
        return datetime.now().replace(year=year, month=month).strftime("%B, %Y")

    @property
    def render_file(self):
        return mark_safe('<a class="inline-link" href="' + reverse(
            ExportFileObject.get_route_name(action=ViewActionEnum.Download), kwargs={
                'pks': self.file_id}) + '">' + self.file.name + self.file.extension + '</a>')

    @property
    def render_survey(self):
        return self.survey if self.survey else None

    @classmethod
    def table_columns(cls):
        return 'render_code', 'render_file', 'render_survey', 'format', 'render_month', 'last_updated'

    @classmethod
    def get_manage_buttons(cls):
        return []

    @classmethod
    def get_object_inline_buttons(cls):
        return []

    @classmethod
    def build_report(cls, time_from=0, time_to=0, survey_id=None, encode=False, wards=None):
        report = list()
        var_types = dict()
        var_names = list()
        survey_obj = Survey.objects.using(BWDatabaseRouter.get_export_database_name()).filter(id=survey_id).first()
        all_questions = Question.objects.using(BWDatabaseRouter.get_export_database_name()) \
            .filter(section__survey_id=survey_id) \
            .exclude(group='Family Profile') \
            .order_by('order') \
            .values('pk', 'question_code')
        all_questions = list(all_questions)  # making list from queryset

        family_profile_questions = Question.objects.using(BWDatabaseRouter.get_export_database_name()) \
            .filter(section__survey_id=survey_id, group='Family Profile') \
            .order_by('order').values('pk', 'question_code')
        family_profile_questions = list(family_profile_questions)  # making list from queryset

        headers = [
            'Survey code', 'Survey Time', 'Survey Last Updated Time', 'Division', 'City/Town', 'Ward Number', 'CDC',
            'Primary Group', 'PG Member ID', 'PG Member Status', 'Cluster-ID', 'Cluster name', 'Latitude', 'Longitude',
            'Enumerator Name', 'Enumerator Phone Number'
        ]

        if encode:
            for _h in headers:
                var_types[bw_compress_name(_h)] = 40
                var_names.append(bw_compress_name(_h))

        # all questions except (Family Profile)
        for question in all_questions:
            question_code = question['question_code']
            headers.append(question_code)
            if encode:
                var_types['Question_' + question_code] = 1
                var_names.append('Question_' + question_code)

        headers += MPI_HH_RESOURCE_LIST()
        headers += ['MPI Score']

        var_types[bw_compress_name('MPI Score')] = 20
        var_names.append(bw_compress_name('MPI Score'))

        # Family Profile Heading-Start
        for _index in range(1, FAMILY_MEMBER_LIMIT):
            for question in family_profile_questions:
                _updated_question_code = question['question_code'] + " (Family Profile #%s)" % str(_index)
                _updated_question_code_sav = question['question_code'] + "_Family_Profile_#%s" % str(_index)
                headers.append(_updated_question_code)
                if encode:
                    var_types['Question_' + _updated_question_code_sav] = 1
                    var_names.append('Question_' + _updated_question_code_sav)
        # Family Profile Heading-End

        headers.append('Photos')
        report.append(headers)

        _timestamp_limit = time_to
        _time_from = time_from
        _time_to = (datetime.fromtimestamp(_time_from / 1000) + timedelta(days=1)).timestamp() * 1000

        while _time_to <= _timestamp_limit:
            survey_response_queryset = SurveyResponse.objects.using(BWDatabaseRouter.get_export_database_name()).filter(
                survey_id=survey_id,
                last_updated__gte=_time_from,
                last_updated__lte=_time_to
            )

            # photo ids dictionary Ex: {survey_response_id:[photo_id1, photo_id2, ...]}
            photo_ids_dict = dict()
            survey_response_ids = list(survey_response_queryset.values_list('id', flat=True))
            survey_response_photos_queryset = list(survey_response_queryset.values('id', 'photos'))

            for _data in survey_response_photos_queryset:
                if _data['photos']:
                    if _data['id'] not in photo_ids_dict.keys():
                        photo_ids_dict[_data['id']] = []
                    photo_ids_dict[_data['id']].append(_data['photos'])

            mpi_indicators = MPIIndicator.objects.using(BWDatabaseRouter.get_export_database_name()).filter(
                survey_response__survey_id=survey_id,
                survey_response_id__in=survey_response_ids
            )
            pgmpi_indicators = PGMPIIndicator.objects.using(BWDatabaseRouter.get_export_database_name()).filter(
                survey_response__survey_id=survey_id,
                survey_response_id__in=survey_response_ids
            )
            if wards and wards[0]:  # If no ward is selected, wards list can be: ['']
                if survey_obj.name == 'PG Member Survey Questionnaire':
                    survey_response_queryset = survey_response_queryset.filter(
                        respondent_client__assigned_to__parent__address__geography_id__in=wards)
                else:
                    survey_response_queryset = survey_response_queryset.filter(
                        respondent_unit__address__geography__parent__parent_id__in=wards)
                mpi_indicators = mpi_indicators.filter(
                    survey_response__respondent_unit__address__geography__parent__parent_id__in=wards)
                pgmpi_indicators = pgmpi_indicators.filter(
                    survey_response__respondent_client__assigned_to__parent__address__geography_id__in=wards)

            if survey_obj.name == 'PG Member Survey Questionnaire':
                all_responses = survey_response_queryset.values(
                    'pk', 'code',
                    'created_by__name', 'created_by__user__username',  # Enumerator's Name, Phone Number
                    'location__latitude', 'location__longitude',  # Location
                    'date_created', 'last_updated',
                    'respondent_client__assigned_code', 'respondent_client__name',  # PG Member
                    'respondent_client__status',  # PG Member Status
                    'respondent_client__assigned_to__name',  # PG
                    'respondent_client__assigned_to__parent__name',  # CDC
                    'respondent_client__assigned_to__parent__parent__assigned_code',  # CDC cluster ID
                    'respondent_client__assigned_to__parent__parent__name',  # CDC cluster Name
                    'respondent_client__assigned_to__parent__address__geography__name',  # Ward
                    'respondent_client__assigned_to__parent__address__geography__parent__name',  # City Corporation
                    'respondent_client__assigned_to__parent__address__geography__parent__parent__name',  # Division
                )
            else:
                all_responses = survey_response_queryset.values(
                    'pk', 'code',
                    'created_by__name', 'created_by__user__username',  # Enumerator's Name, Phone Number
                    'location__latitude', 'location__longitude',  # Location
                    'date_created', 'respondent_unit__assigned_code', 'respondent_unit__name',  # Household
                    'respondent_unit__address__geography__name',  # Poor Settlement
                    'respondent_unit__address__geography__parent__name',  # Mahalla
                    'respondent_unit__address__geography__parent__parent__name',  # Ward
                    'respondent_unit__address__geography__parent__parent__parent__name',  # City Corporation
                    'respondent_unit__address__geography__parent__parent__parent__parent__name',  # Division
                )

            all_responses = list(all_responses)  # making queryset to list
            mpi_indicators = list(mpi_indicators.values('survey_response_id', 'mpi_score'))
            pgmpi_indicators = list(pgmpi_indicators.values('survey_response_id', 'mpi_score'))
            mpi_dict = dict()
            pgmpi_dict = dict()
            if survey_obj.name == 'PG Member Survey Questionnaire':
                for pgmpi in pgmpi_indicators:
                    pgmpi_dict[pgmpi['survey_response_id']] = pgmpi['mpi_score']
            else:
                for mpi in mpi_indicators:
                    mpi_dict[mpi['survey_response_id']] = mpi['mpi_score']

            question_response_queryset = QuestionResponse.objects.using(BWDatabaseRouter.get_export_database_name()) \
                .filter(
                section_response__survey_response__survey_id=survey_id,
                section_response__survey_response_id__in=survey_response_ids
            ).exclude(question__group='Family Profile')

            family_profile_question_response_queryset = \
                QuestionResponse.objects.using(BWDatabaseRouter.get_export_database_name()).filter(
                    section_response__survey_response__survey_id=survey_id,
                    question__group='Family Profile',
                    section_response__survey_response_id__in=survey_response_ids
                )

            if wards and wards[0]:  # For no ward selected, wards list can be: ['']
                if survey_obj.name == 'PG Member Survey Questionnaire':
                    question_response_queryset = question_response_queryset.filter(
                        section_response__survey_response__respondent_client__assigned_to__parent__address__geography_id__in=wards)
                    family_profile_question_response_queryset = family_profile_question_response_queryset.filter(
                        section_response__survey_response__respondent_client__assigned_to__parent__address__geography_id__in=wards)
                else:
                    question_response_queryset = question_response_queryset.filter(
                        section_response__survey_response__respondent_unit__address__geography__parent__parent_id__in=wards)
                    family_profile_question_response_queryset = family_profile_question_response_queryset.filter(
                        section_response__survey_response__respondent_unit__address__geography__parent__parent_id__in=wards)

            question_responses = question_response_queryset.order_by('date_created').values(
                'pk', 'section_response__survey_response_id', 'index', 'question_id',
                'answer_text', 'question__question_type'
            )
            question_responses = list(question_responses)  # making queryset to list

            family_profile_question_responses = family_profile_question_response_queryset.order_by(
                'date_created').values(
                'pk', 'section_response__survey_response_id', 'index', 'question_id',
                'answer_text', 'question__question_type'
            )
            family_profile_question_responses = list(family_profile_question_responses)  # making queryset to list

            question_response_dict = dict()
            for question_response in question_responses:
                survey_response = question_response['section_response__survey_response_id']
                if survey_response not in question_response_dict.keys():
                    question_response_dict[survey_response] = dict()
                question_id = question_response['question_id']
                if question_id not in question_response_dict[survey_response].keys():
                    question_response_dict[survey_response][question_id] = list()

                if question_response['question__question_type'] != QuestionTypeEnum.MultipleSelectInput.value:
                    question_response_dict[survey_response][question_id] = [question_response]
                else:
                    question_response_dict[survey_response][question_id].append(question_response)

            # Family Profile data set -Start
            family_profile_question_response_dict = dict()
            for family_profile_question_response in family_profile_question_responses:
                survey_response = family_profile_question_response['section_response__survey_response_id']
                if survey_response not in family_profile_question_response_dict.keys():
                    family_profile_question_response_dict[survey_response] = dict()
                question_id = family_profile_question_response['question_id']
                if question_id not in family_profile_question_response_dict[survey_response].keys():
                    family_profile_question_response_dict[survey_response][question_id] = list()

                family_profile_question_response_dict[survey_response][question_id].append(
                    family_profile_question_response
                )
            # Family Profile data set -End

            cdc_cluster_id = ''
            cdc_cluster_name = ''
            for response in all_responses:
                photo_ids = photo_ids_dict.get(response['pk'])
                photos_url = ''
                if photo_ids:
                    for p_id in photo_ids:
                        relative_url = ImageFileObject.objects.using(
                            BWDatabaseRouter.get_export_database_name()
                        ).get(pk=p_id).relative_url

                        if relative_url:
                            if not S3_STATIC_ENABLED:
                                photo_href = settings.SITE_ROOT + relative_url[1:]
                            else:
                                photo_href = relative_url
                            photos_url += photo_href + '\n '

                if survey_obj.name == 'PG Member Survey Questionnaire':
                    row = [
                        response['code'],  # survey response code
                        # survey response time
                        Clock.get_user_local_time(response['date_created']).strftime(
                            "%d/%m/%Y - %I:%M %p") if response['date_created'] else 'N/A',
                        # survey response update time
                        Clock.get_user_local_time(response['last_updated']).strftime(
                            "%d/%m/%Y - %I:%M %p") if response['last_updated'] else 'N/A',
                        response['respondent_client__assigned_to__parent__address__geography__parent__parent__name'],
                        # Division
                        response['respondent_client__assigned_to__parent__address__geography__parent__name'],
                        # City Corporation
                        response['respondent_client__assigned_to__parent__address__geography__name'],  # Ward
                        response['respondent_client__assigned_to__parent__name'],  # CDC
                        response['respondent_client__assigned_to__name'],  # PG
                        "'" + response['respondent_client__assigned_code'],  # PGM ID
                        response['respondent_client__status'],  # PGM Status
                        response['respondent_client__assigned_to__parent__parent__assigned_code'],  # CDC cluster ID
                        response['respondent_client__assigned_to__parent__parent__name'],  # CDC cluster Name
                        response['location__latitude'],  # Latitude
                        response['location__longitude'],  # Longitude
                        response['created_by__name'],  # Enumerator Name
                        response['created_by__user__username'],  # Enumerator Phone Number
                    ]
                else:
                    row = [
                        response['code'],  # survey response code
                        response['respondent_unit__address__geography__parent__parent__parent__parent__name'],
                        # Division
                        response['respondent_unit__address__geography__parent__parent__parent__name'],
                        # City Corporation
                        response['respondent_unit__address__geography__parent__parent__name'],  # Ward
                        response['respondent_unit__address__geography__parent__name'],  # Mahalla
                        response['respondent_unit__address__geography__name'],  # Poor Settlement
                        response['respondent_unit__assigned_code'],  # Household Code
                        cdc_cluster_id,
                        cdc_cluster_name,
                        response['location__latitude'],  # Latitude
                        response['location__longitude'],  # Longitude
                        response['created_by__name'],  # Enumerator Name
                        response['created_by__user__username'],  # Enumerator Phone Number
                    ]
                if encode:
                    row = [str(v).encode() for v in row]

                question_index = 0
                for question in all_questions:
                    question_code = all_questions[question_index]['question_code']
                    _val = ''
                    if response['pk'] in question_response_dict.keys() and \
                            question['pk'] in question_response_dict[response['pk']].keys():
                        _val = ', '.join([question_response['answer_text'] for question_response in
                                          question_response_dict[response['pk']][question['pk']]])
                    row.append(_val)
                    if encode:
                        _val = _val.encode()
                        _len = var_types['Question_' + question_code]
                        var_types['Question_' + question_code] = max(_len, len(_val))
                    question_index += 1

                # Resource Question Response : Start Here
                resources = list(QuestionResponse.objects.using(
                    BWDatabaseRouter.get_export_database_name()
                ).filter(
                    section_response__survey_response_id=response['pk'],
                    question__question_code='5.8'
                ).values_list('answer_text', flat=True))

                for mpi_hh_resource in MPI_HH_RESOURCE_LIST():
                    row.append('Yes' if mpi_hh_resource in resources else 'No')
                # Resource Question Response : End Here

                mpi_score = mpi_dict[response['pk']] if response['pk'] in mpi_dict.keys() else '0'
                pgmpi_score = pgmpi_dict[response['pk']] if response['pk'] in pgmpi_dict.keys() else '0'
                if pgmpi_score is not None:
                    row.append(str(pgmpi_score).encode() if encode else str(pgmpi_score))
                else:
                    row.append(str(mpi_score).encode() if encode else str(mpi_score))

                # Family Profile -Start
                for _index in range(1, FAMILY_MEMBER_LIMIT):
                    family_profile_question_index = 0
                    for family_profile_question in family_profile_questions:
                        _val = ''
                        family_profile_question_code = family_profile_questions[family_profile_question_index][
                            'question_code']
                        _updated_question_code = family_profile_question_code + " (Family Profile #%s)" % str(_index)
                        _updated_question_code_sav = family_profile_question_code + "_Family_Profile_#%s" % str(_index)
                        if response['pk'] in family_profile_question_response_dict.keys() and \
                                family_profile_question['pk'] in family_profile_question_response_dict[
                            response['pk']].keys():
                            _val = ', '.join(
                                set([family_profile_question_response['answer_text'] for
                                     family_profile_question_response in
                                     family_profile_question_response_dict[response['pk']][
                                         family_profile_question['pk']]
                                     if family_profile_question_response['index'] == _index])
                            )
                        row.append(_val)
                        if encode:
                            _val = _val.encode()
                            _len = var_types['Question_' + _updated_question_code_sav]
                            var_types['Question_' + _updated_question_code_sav] = max(_len, len(_val))
                        family_profile_question_index += 1
                # Family Profile -End

                row.append(photos_url)
                report.append(row)

            _time_from = _time_to
            _time_to = (datetime.fromtimestamp(_time_to / 1000) + timedelta(days=1)).timestamp() * 1000

        if encode:
            return report, var_names, var_types
        return report

    @classmethod
    def generate_sav(cls, time_from, time_to, survey_id, year, month_name, export_file_object=None, wards=None,
                     filename=None):
        """
        Generate SAV format file
        :param time_from:
        :param time_to:
        :param survey_id:
        :param year:
        :param month_name:
        :param export_file_object:
        :param wards:
        :param filename:
        :return:
        """
        try:
            path = os.path.join(EXPORT_FILE_ROOT)
            if not os.path.exists(path):
                os.makedirs(path)

            survey_obj = Survey.objects.using(BWDatabaseRouter.get_export_database_name()).get(id=survey_id)
            survey_name = survey_obj.name.rsplit(' Survey Questionnaire', 1)[0]

            if year:
                dest_filename = '{}SurveyResponses_{}_{}'.format(survey_name.replace(' ', '_'), month_name, year)
            else:
                dest_filename = '{}SurveyResponses_{}'.format(survey_name.replace(' ', '_'), month_name, year)

            if filename:
                dest_filename = filename

            file_path = path + os.sep + dest_filename + '.sav'

            if S3_STATIC_ENABLED:
                from config.aws_s3_config import STATIC_EXPORT_MEDIA_DIRECTORY
                # firstly remove the file from local directory
                if os.path.isfile(file_path):
                    os.remove(file_path)

                try:
                    # download content from S3
                    s3_file_name = STATIC_EXPORT_MEDIA_DIRECTORY + "/" + str(dest_filename) + '.sav'
                    s3_file_path = s3_file_name.replace(MEDIA_DIRECTORY, '', 1)
                    FilePathHandler.get_absolute_path_from_file_path(s3_file_path, None)
                except:
                    pass

            report, var_names, var_types = cls.build_report(
                time_from=time_from, time_to=time_to,
                survey_id=survey_id, encode=True, wards=wards
            )
            data = report[1:]

            with SavWriter(file_path, var_names, var_types) as writer:
                for record in data:
                    writer.writerow(record)

            # Uploading the exported file to AMAZON S3
            if S3_STATIC_ENABLED:
                from config.aws_s3_config import STATIC_EXPORT_MEDIA_DIRECTORY
                try:
                    with open(file_path, 'rb') as content_file:
                        content = content_file.read()
                        s3_file_name = STATIC_EXPORT_MEDIA_DIRECTORY + "/" + str(dest_filename) + '.sav'
                        file_path = s3_file_name.replace(MEDIA_DIRECTORY, '', 1)
                        AWSFileWriter.upload_file_with_content(file_name=s3_file_name, content=content)

                    # after successfully upload to AWS S3, remove local file
                    os.remove(file_path)
                except Exception as exp:
                    ErrorLog.log(exp=exp)

            if not export_file_object:
                export_file_object = ExportFileObject()
                export_file_object.path = file_path
                export_file_object.name = dest_filename
                export_file_object.file = file_path
                export_file_object.extension = '.sav'
                export_file_object.organization = Organization.get_organization_from_cache()
                export_file_object.save(using=MC_WRITE_DATABAE_NAME)
            return export_file_object
        except Exception as exp:
            ErrorLog.log(exp)
        return None

    @classmethod
    def generate_excel(cls, time_from, time_to, survey_id, year, month_name, export_file_object=None, wards=None,
                       filename=None, mode='a'):
        """
        Generate CSV format file in append mode
        :param time_from:
        :param time_to:
        :param survey_id:
        :param year:
        :param month_name:
        :param export_file_object:
        :param wards:
        :param filename:
        :param mode:
        :return:
        """
        try:
            path = os.path.join(EXPORT_FILE_ROOT)
            if not os.path.exists(path):
                os.makedirs(path)

            survey_obj = Survey.objects.using(BWDatabaseRouter.get_export_database_name()).get(id=survey_id)
            survey_name = survey_obj.name.rsplit(' Survey Questionnaire', 1)[0]

            if year:
                dest_filename = '{}SurveyResponses_{}_{}'.format(survey_name.replace(' ', '_'), month_name, year)
            else:
                dest_filename = '{}SurveyResponses_{}'.format(survey_name.replace(' ', '_'), month_name, year)
            if filename:
                dest_filename = filename
            file_path = path + os.sep + dest_filename + '.csv'

            if S3_STATIC_ENABLED:
                from config.aws_s3_config import STATIC_EXPORT_MEDIA_DIRECTORY
                # firstly remove the file from local directory
                if os.path.isfile(file_path):
                    os.remove(file_path)

                try:
                    # download content from S3
                    s3_file_name = STATIC_EXPORT_MEDIA_DIRECTORY + "/" + str(dest_filename) + '.csv'
                    s3_file_path = s3_file_name.replace(MEDIA_DIRECTORY, '', 1)
                    FilePathHandler.get_absolute_path_from_file_path(s3_file_path, None)
                except:
                    pass

            skip_header = False
            if os.path.isfile(file_path):
                skip_header = True

            csv_file = open(file_path, mode, encoding='utf-8')

            if mode == 'w':
                skip_header = False
                csv_file.write('\ufeff')

            _timestamp_limit = time_to
            _time_from = time_from
            _time_to = int((datetime.fromtimestamp(_time_from / 1000) + timedelta(days=1)).timestamp()) * 1000

            while _time_from <= _timestamp_limit:
                print('Handling Survey:{0}, File Name:{1}, Date:{2}'.format(
                    survey_id, filename,
                    datetime.fromtimestamp(_time_from / 1000).date(),
                ))

                report = cls.build_report(time_from=_time_from, time_to=_time_to, survey_id=survey_id, wards=wards)
                if skip_header:
                    report = report[1:]

                for _row in report:
                    row_as_str = ','.join(['"{}"'.format(_val) for _val in _row]) + '\n'
                    csv_file.write(row_as_str)
                _time_from = _time_to
                _time_to = (datetime.fromtimestamp(_time_to / 1000) + timedelta(days=1)).timestamp() * 1000
                skip_header = True

            csv_file.close()

            # Uploading the exported file to AMAZON S3
            if S3_STATIC_ENABLED:
                from config.aws_s3_config import STATIC_EXPORT_MEDIA_DIRECTORY
                try:
                    with open(file_path, 'rb') as content_file:
                        content = content_file.read()
                        s3_file_name = STATIC_EXPORT_MEDIA_DIRECTORY + "/" + str(dest_filename) + '.csv'
                        file_path = s3_file_name.replace(MEDIA_DIRECTORY, '', 1)
                        AWSFileWriter.upload_file_with_content(file_name=s3_file_name, content=content)

                except Exception as exp:
                    ErrorLog.log(exp=exp)

            if not export_file_object:
                export_file_object = ExportFileObject()
                export_file_object.path = file_path
                export_file_object.name = dest_filename
                export_file_object.file = file_path
                export_file_object.extension = '.csv'
                export_file_object.organization = Organization.get_organization_from_cache()
                export_file_object.save(using=MC_WRITE_DATABAE_NAME)
            return export_file_object
        except Exception as exp:
            ErrorLog.log(exp)
        return None


     # My Edit
    @classmethod
    def generate_excel_instants(cls, time_from, time_to, survey_id, year, month_name, export_file_object=None, wards=None,
                       filename=None, mode='a'):
        """
        Generate CSV format file in append mode
        :param time_from:
        :param time_to:
        :param survey_id:
        :param year:
        :param month_name:
        :param export_file_object:
        :param wards:
        :param filename:
        :param mode:
        :return:
        """
        try:
            path = os.path.join(EXPORT_FILE_ROOT)
            if not os.path.exists(path):
                os.makedirs(path)

            survey_obj = Survey.objects.using(BWDatabaseRouter.get_export_database_name()).get(id=survey_id)
            survey_name = survey_obj.name.rsplit(' Survey Questionnaire', 1)[0]

            if year:
                dest_filename = '{}SurveyResponses_{}_{}'.format(survey_name.replace(' ', '_'), month_name, year)
            else:
                dest_filename = '{}SurveyResponses_{}'.format(survey_name.replace(' ', '_'), month_name, year)
            if filename:
                dest_filename = filename
            file_path = path + os.sep + dest_filename + '.csv'

            if S3_STATIC_ENABLED:
                from config.aws_s3_config import STATIC_EXPORT_MEDIA_DIRECTORY
                # firstly remove the file from local directory
                if os.path.isfile(file_path):
                    os.remove(file_path)

                try:
                    # download content from S3
                    s3_file_name = STATIC_EXPORT_MEDIA_DIRECTORY + "/" + str(dest_filename) + '.csv'
                    s3_file_path = s3_file_name.replace(MEDIA_DIRECTORY, '', 1)
                    FilePathHandler.get_absolute_path_from_file_path(s3_file_path, None)
                except:
                    pass

            skip_header = False
            if os.path.isfile(file_path):
                skip_header = True

            csv_file = open(file_path, mode, encoding='utf-8')

            if mode == 'w':
                skip_header = False
                csv_file.write('\ufeff')

            _timestamp_limit = time_to
            _time_from = time_from
            _time_to = int((datetime.fromtimestamp(_time_from / 1000) + timedelta(days=1)).timestamp()) * 1000

            while _time_from <= _timestamp_limit:
                print('Handling Survey:{0}, File Name:{1}, Date:{2}'.format(
                    survey_id, filename,
                    datetime.fromtimestamp(_time_from / 1000).date(),
                ))

                report = cls.build_report(time_from=_time_from, time_to=_time_to, survey_id=survey_id, wards=wards)
                if skip_header:
                    report = report[1:]

                for _row in report:
                    row_as_str = ','.join(['"{}"'.format(_val) for _val in _row]) + '\n'
                    csv_file.write(row_as_str)
                _time_from = _time_to
                _time_to = (datetime.fromtimestamp(_time_to / 1000) + timedelta(days=1)).timestamp() * 1000
                skip_header = True
            
            csv_file.close()

             # Uploading the exported file to AMAZON S3
            if S3_STATIC_ENABLED:
                from config.aws_s3_config import STATIC_EXPORT_MEDIA_DIRECTORY
                with open(file_path, 'rb') as content_file:
                    content = content_file.read()
                    s3_file_name = STATIC_EXPORT_MEDIA_DIRECTORY + "/" + str(dest_filename) + '.csv'
                    relative_file_path = s3_file_name.replace(MEDIA_DIRECTORY, '', 1)
                    AWSFileWriter.upload_file_with_content(file_name=s3_file_name, content=content)

                # get local file size in bytes
                local_file_size = os.path.getsize(file_path)
                local_file_last_modified = os.path.getmtime(file_path)

                # get S3 file size in bytes
                s3_file_name = STATIC_EXPORT_MEDIA_DIRECTORY + "/" + str(dest_filename) + '.csv'
                s3_file_meta = AWSFileWriter.get_file_meta(file_name=s3_file_name)
                s3_file_size = s3_file_meta.content_length
                s3_file_last_modified = s3_file_meta.last_modified

                upload_attempts = 0
                while local_file_size == 0 or s3_file_size == 0 or local_file_size != s3_file_size:
                    upload_attempts += 1
                    if upload_attempts > 2:  # maximum additional tries two times
                        break

                    # create an error log entry
                    _msg = "Model Name: {0}, File Name: {1}, Source file size is {2} bytes, generated on {3}. Destination file size in S3 is {4} bytes and last modified at {5}".format(
                        cls.__name__,
                        str(dest_filename) + '.csv',
                        local_file_size,
                        Clock.get_user_local_time(local_file_last_modified * 1000).strftime("%d/%m/%Y - %I:%M %p"),
                        s3_file_size,
                        s3_file_last_modified
                    )
                    ErrorLog.log(exp=_msg)

                    try:
                        with open(file_path, 'rb') as content_file:
                            content = content_file.read()
                            s3_file_name = STATIC_EXPORT_MEDIA_DIRECTORY + "/" + str(dest_filename) + '.csv'
                            relative_file_path = s3_file_name.replace(MEDIA_DIRECTORY, '', 1)
                            AWSFileWriter.upload_file_with_content(file_name=s3_file_name, content=content)
                    except Exception as exp:
                        ErrorLog.log(exp=exp)

                    # get local file size in bytes
                    local_file_size = os.path.getsize(file_path)
                    local_file_last_modified = os.path.getmtime(file_path)

                    # get S3 file size in bytes
                    s3_file_name = STATIC_EXPORT_MEDIA_DIRECTORY + "/" + str(dest_filename) + '.csv'
                    s3_file_meta = AWSFileWriter.get_file_meta(file_name=s3_file_name)
                    s3_file_size = s3_file_meta.content_length
                    s3_file_last_modified = s3_file_meta.last_modified

            if not export_file_object:
                export_file_object = ExportFileObject()
                export_file_object.path = relative_file_path
                export_file_object.name = dest_filename
                export_file_object.file = relative_file_path
                export_file_object.extension = '.csv'
                export_file_object.organization = Organization.get_organization_from_cache()
                export_file_object.save(using=MC_WRITE_DATABAE_NAME)

            return export_file_object



        except Exception as exp:
            ErrorLog.log(exp)
        return None


      # My Edit
    @classmethod
    def generate_excel_instant(cls, time_from, time_to, survey_id, year, month_name, export_file_object=None, wards=None,
                       filename=None, mode='a'):
        """
        Generate CSV format file in append mode
        :param time_from:
        :param time_to:
        :param survey_id:
        :param year:
        :param month_name:
        :param export_file_object:
        :param wards:
        :param filename:
        :param mode:
        :return:
        """
        

        _timestamp_limit = time_to
        _time_from = time_from
        _time_to = int((datetime.fromtimestamp(_time_from / 1000) + timedelta(days=1)).timestamp()) * 1000

        while _time_from <= _timestamp_limit:
            print('Handling Survey:{0}, File Name:{1}, Date:{2}'.format(
                survey_id, filename,
                datetime.fromtimestamp(_time_from / 1000).date(),
            ))

        report = cls.build_report(time_from=_time_from, time_to=_time_to, survey_id=survey_id, wards=wards)
        

        echo_buffer = Echo()
        csv_writer = csv.writer(echo_buffer)

        # By using a generator expression to write each row in the queryset
        # python calculates each row as needed, rather than all at once.
        # Note that the generator uses parentheses, instead of square
        # brackets – ( ) instead of [ ].
        rows = (csv_writer.writerow(row) for row in report)

        response = StreamingHttpResponse(rows, content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="users.csv"'
        return response

             # Uploading the exported file to AMAZON S3
            

    



    @classmethod
    def generate_complete_export_file(cls, survey_id=None):
        """
        Generate the whole DataSet
        :return: 
        """
        print("Generating Excel...")
        recorded_time = SurveyResponse.objects.using(BWDatabaseRouter.get_export_database_name()).filter(
            survey_id=survey_id).aggregate(Min('date_created'))[
            'date_created__min']
        if recorded_time is None:
            recorded_time = 0
        current_time = datetime.now().timestamp() * 1000
        excel_export_file, created = cls.objects.get_or_create(year=0, month=0, format='Excel')

        excel_file_obj = cls.generate_excel(
            time_from=recorded_time, time_to=current_time, survey_id=survey_id, year=0, month_name='All_Survey',
            export_file_object=None)
        excel_export_file.file = excel_file_obj
        excel_export_file.save()
        print("...Generated")

        # print("Generating SPSS...")
        # spss_export_file, created = cls.objects.get_or_create(year=0, month=0, format='SPSS')
        # spss_file_obj = cls.generate_sav(
        #     time_from=recorded_time, time_to=current_time, survey_id=survey_id, year=0, month_name='All_Survey',
        #     export_file_object=None)
        # spss_export_file.file = spss_file_obj
        # spss_export_file.save()
        # print("...Generated")

    @classmethod
    def perform_routine_export_files_generation(cls, time=None, survey_id=None):
        """
        Generate Survey Response excel file (If file already exist, then update)
        :param time: (optional) not used.
        :return:
        """
        generation_time = datetime.now() - timedelta(days=1)
        cls.generate_export_files_in_given_time(generation_time=generation_time, survey_id=survey_id)

    @classmethod
    def generate_export_files_in_given_time(cls, generation_time, survey_id=None, mode='a'):
        """
        Generate Survey Response excel file in a given time
        :param generation_time: Time at which the monthly report is generated. It is good to be the last day of the month
        :param mode: file open mode
        :return:
        """
        month_start = generation_time.replace(day=1, hour=0, minute=0, second=0).timestamp() * 1000

        next_year = generation_time.year
        next_month = generation_time.month + 1
        if next_month > 12:
            next_month = 1
            next_year += 1
        time_to = (generation_time.replace(year=next_year, month=next_month, day=1) - timedelta(days=1)).replace(
            hour=23, minute=59, second=59).timestamp() * 1000

        year = int(generation_time.strftime("%Y"))  # Clock.millisecond_to_date_str(time_to, _format="%Y")
        month = int(generation_time.strftime("%m"))  # Clock.millisecond_to_date_str(time_to, _format="%B")
        month_name = generation_time.strftime("%B")  # Clock.millisecond_to_date_str(time_to, _format="%B")

        for export_file_type in ['Excel', ]:
            bw_debug('Preparing ' + export_file_type)
            existing_file = cls.objects.filter(year=year, survey_id=survey_id, month=month,
                                               format=export_file_type).order_by(
                '-date_created').first()
            if existing_file:
                last_updated = existing_file.last_updated if export_file_type == 'Excel' else month_start
                usable_file = existing_file.file
            else:
                last_updated = month_start
                usable_file = None
                existing_file = cls(format=export_file_type, year=year, month=month)
                existing_file.survey_id = survey_id
                existing_file.format = export_file_type
                existing_file.year = year
                existing_file.month = month
            if export_file_type == 'Excel':
                file_obj = cls.generate_excel(
                    survey_id=survey_id,
                    time_from=last_updated, time_to=time_to, year=year,
                    month_name=month_name, export_file_object=usable_file, mode=mode
                )
            else:
                file_obj = cls.generate_sav(
                    survey_id=survey_id,
                    time_from=last_updated, time_to=time_to, year=year,
                    month_name=month_name, export_file_object=usable_file
                )
            existing_file.file = file_obj
            existing_file.save()
            bw_debug('...Prepared')

  # My Edit
class Echo:
    def write(self, value):
        return value