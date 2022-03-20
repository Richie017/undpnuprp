import hashlib
import os
from collections import OrderedDict
from random import random
import string
from turtle import st

from crequest.middleware import CrequestMiddleware
from django.conf import settings

from blackwidow.core.managers.archivemanager import ArchiveManager
from blackwidow.core.models import ErrorLog
from blackwidow.core.models.file.exportfileobject import ExportFileObject
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.extensions.clock import Clock
from blackwidow.engine.file_handlers.aws_file_writer import AWSFileWriter
from blackwidow.engine.file_handlers.file_path_handler import FilePathHandler
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from config.aws_s3_config import MEDIA_DIRECTORY
from undp_nuprp.survey.models.export.survey_response_generated_file import SurveyResponseGeneratedFile
from undp_nuprp.reports.models.base.base import Report
from undp_nuprp.survey.models.schedulers.survey_export_task_queue import SurveyExportTaskQueue

from django.http import HttpResponse

import random

EXPORT_FILE_ROOT = settings.EXPORT_FILE_ROOT
STATIC_EXPORT_URL = settings.STATIC_EXPORT_URL
S3_STATIC_ENABLED = settings.S3_STATIC_ENABLED

__author__ = 'Ziaul Haque'


@decorate(is_object_context,
          route(route='survey-data-export-report', group='Download Data', group_order=4,
                module=ModuleEnum.Administration,
                display_name="Survey Data Export", item_order=4))
class SurveyDataExportReport(Report):
    class Meta:
        proxy = True
        app_label = 'survey'

    @classmethod
    def build_report(cls, divisions=None, cities=None, surveys=None, wards=None, domain=None, time_from=None,
                     time_to=None):
        # return HttpResponse(str("abcd"))   
        c_request = CrequestMiddleware.get_request()
        _user = c_request.c_user
        _hashable_text = ''
        _hashable_text += str(time_from)
        _hashable_text += str(time_to)
        if divisions:
            _hashable_text += ','.join(map(str, divisions))
        if surveys:
            _hashable_text += ','.join(map(str, str(surveys)))
        if cities:
            _hashable_text += ','.join(map(str, cities))
        if wards:
            _hashable_text += ','.join(map(str, wards))
        _hash = hashlib.md5(_hashable_text.encode('utf-8')).hexdigest()
        survey_response_generated_files = ExportFileObject.objects.using(
            BWDatabaseRouter.get_read_database_name()).filter(name=_hash)
        response = OrderedDict()
        if survey_response_generated_files.exists():
            download_url = STATIC_EXPORT_URL
            path = os.path.join(EXPORT_FILE_ROOT)
            if not os.path.exists(path):
                os.makedirs(path)
            _file_exists = True
            _download_link = None
            if survey_response_generated_files.count() > 1:
                temporary_files = []
                if S3_STATIC_ENABLED:
                    for x in survey_response_generated_files:
                        # download files from S3
                        temporary_files.append(FilePathHandler.get_absolute_path(x.file))

                file_name = 'SurveyResponses_' + str(Clock.timestamp())
                files = list()
                for x in survey_response_generated_files:
                    if os.path.isfile(path + os.sep + x.name + x.extension):
                        files.append((x.path, x.name + x.extension))
                ArchiveManager.zip_files(files, os.path.join(path, file_name))

                # Uploading the exported file to AMAZON S3
                if S3_STATIC_ENABLED:
                    from config.aws_s3_config import STATIC_EXPORT_MEDIA_DIRECTORY
                    try:
                        file_path = path + os.sep + str(file_name) + '.zip'
                        with open(file_path, 'rb') as content_file:
                            content = content_file.read()
                            s3_file_name = STATIC_EXPORT_MEDIA_DIRECTORY + "/" + str(file_name) + '.zip'
                            file_path = s3_file_name.replace(MEDIA_DIRECTORY, '', 1)
                            AWSFileWriter.upload_file_with_content(file_name=s3_file_name, content=content)
                        temporary_files.append(file_path)

                        # after successfully upload to AWS S3, remove local file
                        for temp_file in temporary_files:
                            try:
                                os.remove(temp_file)
                            except:
                                pass
                    except Exception as exp:
                        ErrorLog.log(exp=exp)

                _download_link = download_url + file_name + '.zip'
            else:
                _generated_file = survey_response_generated_files.first()
                if S3_STATIC_ENABLED or os.path.isfile(
                        path + os.sep + _generated_file.name + _generated_file.extension):
                    _download_link = '/export-files/download/' + str(_generated_file.pk)
                else:
                    _file_exists = False
            if _file_exists:
                response['url'] = _download_link
                response['success'] = True
            else:
                response['success'] = False
                # create survey export task queue
                domain_param = ''
                if domain:
                    domain_param = ','.join(map(str, list(domain)))
                query_param = str(time_from) + ',' + str(time_to) + ',' + str(surveys) + ',' + domain_param
                SurveyExportTaskQueue.create_task_queue(_name=_hash, _query_params=query_param, _user=_user)
        else:
            response['success'] = False
            # create survey export task queue
            domain_param = ''
            if domain:
                domain_param = ','.join(map(str, list(domain)))
            query_param = str(time_from) + ',' + str(time_to) + ',' + str(surveys) + ',' + domain_param
            SurveyExportTaskQueue.create_task_queue(_name=_hash, _query_params=query_param, _user=_user)
        return response

    @classmethod
    def build_instant(cls, divisions=None, cities=None, surveys=None, wards=None, domain=None, time_from=None,time_to=None):
        # return HttpResponse(str("gdhgdhgd"))
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))    
        SurveyResponseGeneratedFile.generate_excel(
                    time_from=time_from, time_to=time_to, survey_id=surveys, year=None, month_name=None,
                    wards=wards, filename=str(ran)+str(time_from)+"-"+str(time_to), mode='w'
                ),
     