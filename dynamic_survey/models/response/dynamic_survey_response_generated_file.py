import os
from collections import OrderedDict
from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.urls.base import reverse
from django.utils.safestring import mark_safe

from blackwidow.core.models import ImageFileObject
from blackwidow.core.models.contracts.base import DomainEntity
from blackwidow.core.models.file.exportfileobject import ExportFileObject
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.clock import Clock
from blackwidow.engine.file_handlers.aws_file_writer import AWSFileWriter
from blackwidow.engine.file_handlers.file_path_handler import FilePathHandler
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from config.aws_s3_config import MEDIA_DIRECTORY
from config.database import MC_WRITE_DATABAE_NAME
from dynamic_survey.enums.dynamic_survey_question_type_enum import DynamicSurveyQuestionTypeEnum
from dynamic_survey.enums.dynamic_survey_status_enum import DynamicSurveyStatusEnum
from dynamic_survey.models import DynamicQuestion, DynamicQuestionResponse
from dynamic_survey.models.design.dynamic_survey import DynamicSurvey
from undp_nuprp.nuprp_admin.utils.enums.question_type_enum import QuestionTypeEnum

EXPORT_FILE_ROOT = settings.EXPORT_FILE_ROOT
S3_STATIC_ENABLED = settings.S3_STATIC_ENABLED

__author__ = 'Ziaul Haque'


class DynamicSurveyResponseGeneratedFile(DomainEntity):
    survey = models.ForeignKey('dynamic_survey.DynamicSurvey')
    month = models.IntegerField(default=1)
    year = models.IntegerField(default=2017)
    file = models.ForeignKey('core.FileObject', null=True)

    class Meta:
        app_label = 'dynamic_survey'

    @classmethod
    def default_order_by(cls):
        return ['survey', '-year', '-month']

    @property
    def render_month(self):
        return datetime.now().replace(year=self.year, month=self.month).strftime("%B, %Y")

    @property
    def render_file(self):
        return mark_safe('<a class="inline-link" href="' + reverse(
            ExportFileObject.get_route_name(action=ViewActionEnum.Download), kwargs={
                'pks': self.file_id}) + '">' + self.file.name + self.file.extension + '</a>')

    @classmethod
    def table_columns(cls):
        return 'code', 'render_file', 'survey', 'render_month', 'last_updated'

    @classmethod
    def get_manage_buttons(cls):
        return []

    @classmethod
    def get_object_inline_buttons(cls):
        return []

    @classmethod
    def build_report(cls, time_from=0, time_to=0, survey=None):
        report = list()
        survey_id = survey.pk

        survey_questions = DynamicQuestion.objects.using(
            BWDatabaseRouter.get_export_database_name()
        ).filter(section__survey_id=survey_id).values(
            'id', 'question_type', 'parent_id', 'parent__question_code', 'parent__text',
            'question_code', 'text', 'parent__question_type', 'section_id', 'section__name'
        ).order_by('section__order', 'order')

        _section_id_name_dict = OrderedDict()
        _child_grid_ques_dict = OrderedDict()
        _grid_qid_by_index_dict = OrderedDict()
        _question_id_info_dict = OrderedDict()

        for survey_question in survey_questions:
            parent_question_id = survey_question['parent_id']
            section_id = survey_question['section_id']
            section_name = survey_question['section__name']
            question_id = survey_question['id']
            question_code = survey_question['question_code']
            question_text = survey_question['text']
            parent_ques_code = survey_question['parent__question_code']
            parent_ques_text = survey_question['parent__text']
            question_type = survey_question['question_type']
            parent_question_type = survey_question['parent__question_type']

            if section_id not in _section_id_name_dict:
                _section_id_name_dict[section_id] = {
                    'name': section_name,
                    'questions': []
                }

            if parent_question_type == QuestionTypeEnum.DynamicGrid.value:
                if parent_question_id not in _child_grid_ques_dict:
                    _child_grid_ques_dict[parent_question_id] = []
                    _grid_qid_by_index_dict[parent_question_id] = []
                _child_grid_ques_dict[parent_question_id].append(question_id)
            else:
                _section_id_name_dict[section_id]['questions'].append(question_id)

            _question_id_info_dict[question_id] = {
                'question_code': question_code + ' ' + question_text,
                'parent_id': parent_question_id,
                'parent_question_code': (parent_ques_code + ' ' + parent_ques_text)
                if parent_ques_code and parent_ques_text else '',
                'section_id': section_id,
                'section_name': section_name,
                'question_type': question_type,
                'parent_question_type': parent_question_type
            }

        headers = [
            'Survey Time', 'Survey Response Code', 'User Name',
            'User Contact Number', 'Latitude', 'Longitude'
        ]
        _default_headers = [
            'Survey Time', 'Survey Response Code', 'User Name',
            'User Contact Number', 'Latitude', 'Longitude'
        ]

        for _sec_info in _section_id_name_dict.values():
            _questions = _sec_info['questions']
            for q_id in _questions:
                _ques_info = _question_id_info_dict[q_id]
                if _ques_info['question_type'] == DynamicSurveyQuestionTypeEnum.DynamicGrid.value:
                    _grid_ques_ids = _child_grid_ques_dict[q_id]
                    _tot_grid_ques = len(_grid_ques_ids)
                    _grid_ques_inds = _grid_qid_by_index_dict[q_id]
                    if len(_grid_ques_inds):
                        for _indx in sorted(_grid_ques_inds):
                            # headers.append(_ques_info['question_code'] + '#{}'.format(_indx))

                            for _qid in _grid_ques_ids:
                                headers.append(_question_id_info_dict[_qid]['question_code'] + '#{}'.format(_indx))
                    else:
                        # headers.append(_ques_info['question_code'])

                        for _qid in _grid_ques_ids:
                            headers.append(_question_id_info_dict[_qid]['question_code'])
                else:
                    headers.append(_ques_info['question_code'])

        report.append(headers)

        _timestamp_limit = time_to
        _time_from = time_from
        _time_to = (datetime.fromtimestamp(_time_from / 1000) + timedelta(days=1)).timestamp() * 1000

        while _time_to <= _timestamp_limit:
            question_responses = DynamicQuestionResponse.objects.using(
                BWDatabaseRouter.get_export_database_name()
            ).exclude(
                section_response__survey_response__is_deleted=True
            ).filter(
                section_response__survey_response__survey_id=survey_id,
                section_response__survey_response__date_created__gte=_time_from,
                section_response__survey_response__date_created__lte=_time_to
            )

            survey_response_dict = {}
            _sr_ques_index_ans_dict = {}

            survey_basic_information = question_responses.order_by('section_response__survey_response_id').distinct(
                'section_response__survey_response_id').values(
                'section_response__survey_response_id', 'section_response__survey_response__on_spot_creation_time',
                'section_response__survey_response__respondent_client__name',
                'section_response__survey_response__respondent_unit__name',
                'section_response__survey_response__location__latitude',
                'section_response__survey_response__location__longitude', 'created_by__phones__phone',
                'section_response__survey_response__code', 'created_by__name')

            for survey_response in survey_basic_information:
                survey_response_id = survey_response['section_response__survey_response_id']
                survey_time = survey_response['section_response__survey_response__on_spot_creation_time']
                respondent_client = survey_response['section_response__survey_response__respondent_client__name']
                respondent_unit = survey_response['section_response__survey_response__respondent_unit__name']
                latitude = survey_response['section_response__survey_response__location__latitude']
                longitude = survey_response['section_response__survey_response__location__longitude']
                phone = survey_response['created_by__phones__phone']
                survey_response_code = survey_response['section_response__survey_response__code']
                user_name = survey_response['created_by__name']

                survey_response_dict[survey_response_id] = OrderedDict()
                survey_response_dict[survey_response_id]['Survey Time'] = \
                    Clock.get_user_local_time(survey_time).strftime("%d/%m/%Y") if survey_time else None
                survey_response_dict[survey_response_id]['Respondent Client'] = respondent_client
                survey_response_dict[survey_response_id]['respondent_unit'] = respondent_unit
                survey_response_dict[survey_response_id]['Latitude'] = latitude
                survey_response_dict[survey_response_id]['Longitude'] = longitude
                survey_response_dict[survey_response_id]['User Contact Number'] = phone
                survey_response_dict[survey_response_id]['Survey Response Code'] = survey_response_code
                survey_response_dict[survey_response_id]['User Name'] = user_name

            question_responses = question_responses.values(
                'photo_id', 'photo__name', 'question_id', 'answer_text',
                'question__question_type', 'section_response__survey_response_id',
                'index', 'question__parent_id', 'question__parent__text'
            ).order_by('section_response__survey_response_id', 'question__order', 'index', 'answer_text')

            for question_response in question_responses:
                question_id = question_response['question_id']
                parent_question_id = question_response['question__parent_id']
                question_type = question_response['question__question_type']

                if question_type == 'image' and question_response['photo_id']:
                    relative_url = ImageFileObject.objects.using(
                        BWDatabaseRouter.get_export_database_name()
                    ).get(pk=question_response['photo_id']).relative_url
                    if relative_url:
                        if not S3_STATIC_ENABLED:
                            photo_href = settings.SITE_ROOT + relative_url
                            photo_href = photo_href[1:]
                        else:
                            photo_href = relative_url
                        answer = photo_href
                    else:
                        answer = question_response['answer_text']
                else:
                    answer = question_response['answer_text']

                survey_response_id = question_response['section_response__survey_response_id']
                index = question_response['index']

                if parent_question_id in _grid_qid_by_index_dict:
                    if index not in _grid_qid_by_index_dict[parent_question_id]:
                        _grid_qid_by_index_dict[parent_question_id].append(index)

                if survey_response_id not in _sr_ques_index_ans_dict:
                    _sr_ques_index_ans_dict[survey_response_id] = {}

                if question_id not in _sr_ques_index_ans_dict[survey_response_id]:
                    _sr_ques_index_ans_dict[survey_response_id][question_id] = {}

                if index not in _sr_ques_index_ans_dict[survey_response_id][question_id]:
                    _sr_ques_index_ans_dict[survey_response_id][question_id][index] = answer
                else:
                    sep = ', '
                    _sr_ques_index_ans_dict[survey_response_id][question_id][index] += sep + answer

            for _sr_id, sr_info in _sr_ques_index_ans_dict.items():
                row = []
                for h in _default_headers:
                    if _sr_id in survey_response_dict and h in survey_response_dict[_sr_id]:
                        row.append(str(survey_response_dict[_sr_id][h]).strip())
                    else:
                        row.append('')

                for _sec_info in _section_id_name_dict.values():
                    _questions = _sec_info['questions']
                    for q_id in _questions:
                        _ques_info = _question_id_info_dict[q_id]
                        if _ques_info['question_type'] == DynamicSurveyQuestionTypeEnum.DynamicGrid.value:
                            _grid_ques_ids = _child_grid_ques_dict[q_id]
                            _grid_ques_inds = _grid_qid_by_index_dict[q_id]
                            if len(_grid_ques_inds):
                                for ind in sorted(_grid_ques_inds):
                                    for _qid in _grid_ques_ids:
                                        if _qid in sr_info and ind in sr_info[_qid]:
                                            row.append(str(sr_info[_qid][ind]))
                                        else:
                                            row.append('')
                            else:
                                for _qid in _grid_ques_ids:
                                    row.append('')
                        else:
                            row.append(sr_info[q_id][-1].strip() if q_id in sr_info else '')
                report.append(row)

            _time_from = _time_to
            _time_to = (datetime.fromtimestamp(_time_to / 1000) + timedelta(days=1)).timestamp() * 1000

        return report

    @classmethod
    def generate_excel(cls, time_from, time_to, survey_id, year, month_name, export_file_object=None,
                       filename=None, mode='a'):
        """
        Generate CSV format file in append mode
        :param time_from:
        :param time_to:
        :param survey_id:
        :param year:
        :param month_name:
        :param export_file_object:
        :param filename:
        :param mode:
        :return:
        """
        try:
            path = os.path.join(EXPORT_FILE_ROOT)
            if not os.path.exists(path):
                os.makedirs(path)

            if filename:
                dest_filename = filename
            else:
                dest_filename = '{0}_DynamicSurveyResponses_{1}_{2}'.format(survey_id, month_name, year)

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
            survey_obj = DynamicSurvey.objects.using(
                BWDatabaseRouter.get_export_database_name()
            ).filter(id=survey_id).first()

            while _time_from <= _timestamp_limit:
                print('Handling Survey:{0}, Date:{1}'.format(
                    survey_id,
                    datetime.fromtimestamp(_time_from / 1000).date()
                ))
                report = cls.build_report(time_from=_time_from, time_to=_time_to, survey=survey_obj)
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

    @classmethod
    def perform_routine_export_files_generation(cls):
        """
        Generate Dynamic Survey Response excel file (If file already exist, then update)
        :return:
        """
        given_date = (Clock.now() - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        year = given_date.year
        month = given_date.month + 1
        if month > 12:
            month = 1
            year += 1
        given_date = given_date.replace(year=year, month=month)
        given_date -= timedelta(seconds=1)

        month_start = given_date.replace(day=1, hour=0, minute=0, second=0).timestamp() * 1000
        year = int(given_date.strftime("%Y"))  # Clock.millisecond_to_date_str(time_to, _format="%Y")
        month = int(given_date.strftime("%m"))  # Clock.millisecond_to_date_str(time_to, _format="%B")

        survey_id_list = DynamicSurvey.objects.filter(
            status__in=[
                DynamicSurveyStatusEnum.Disabled.value,
                DynamicSurveyStatusEnum.Published.value
            ]
        ).values_list('pk', flat=True)
        for survey_id in survey_id_list:
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

    @classmethod
    def generate_export_files_in_given_time(cls, generation_time, survey_id=None, mode='a', last_generated_timestamp=None):
        """
        Generate Dynamic Survey Response excel file in a given time
        :param generation_time: Time at which the monthly report is generated. It is good to be the last day of the month
        :param survey_id: pk of given dynamic survey
        :param mode: file open mode
        :param last_generated_timestamp: last_updated timestamp of dynamic survey response generated file
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

        print("Dynamic Survey: {0}, Month,Year: {1},{2}".format(survey_id, month_name, year))

        existing_file = cls.objects.filter(
            year=year,
            survey_id=survey_id,
            month=month
        ).order_by('-date_created').first()
        if existing_file:
            last_updated = existing_file.last_updated
            usable_file = existing_file.file
        else:
            last_updated = month_start
            usable_file = None
            existing_file = cls(year=year, month=month, survey_id=survey_id)

        if last_generated_timestamp:
            last_updated = last_generated_timestamp

        file_obj = cls.generate_excel(
            survey_id=survey_id,
            time_from=last_updated, time_to=time_to, year=year,
            month_name=month_name, export_file_object=usable_file, mode=mode
        )

        existing_file.file = file_obj
        existing_file.save()
        print('...Prepared')
