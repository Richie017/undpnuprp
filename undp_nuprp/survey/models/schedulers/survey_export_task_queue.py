from collections import OrderedDict
from datetime import datetime

from django.core.mail.message import EmailMultiAlternatives
from django.db import models

from blackwidow.core.models.email.email_template import EmailTemplate
from blackwidow.core.models.file.exportfileobject import ExportFileObject
from blackwidow.core.models.log.email_log import EmailLog
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.engine.constants.cache_constants import SCHEDULER_TASK_QUEUE_CACHE_KEY, ONE_DAY_TIMEOUT
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import Clock
from blackwidow.engine.managers.cachemanager import CacheManager
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from blackwidow.scheduler.models.task_queue import SchedulerTaskQueue, SchedulerTaskQueueEnum
from config.database import MC_WRITE_DATABAE_NAME
from config.email_config import DEFAULT_FROM_EMAIL
from undp_nuprp.survey.models.export.survey_response_generated_file import SurveyResponseGeneratedFile

__author__ = 'Ziaul Haque'


@decorate(is_object_context,
          route(route='survey-export-task-monitor', group='Other Admin', module=ModuleEnum.Settings,
                display_name='Survey Export Task Monitor')
          )
class SurveyExportTaskQueue(SchedulerTaskQueue):
    query_params = models.CharField(max_length=8000, null=True, default=None)
    start_time = models.BigIntegerField(editable=False, null=True, blank=True)
    completion_time = models.BigIntegerField(editable=False, null=True, blank=True)
    extra_info = models.CharField(max_length=8000, null=True, default=None)

    class Meta:
        app_label = 'survey'

    @property
    def render_performed_on(self):
        return self.render_timestamp(self.date_created)

    @property
    def render_start_time(self):
        if self.start_time:
            return self.render_timestamp(self.start_time)
        return '----'

    @property
    def render_completion_time(self):
        if self.completion_time:
            return self.render_timestamp(self.completion_time)
        return '----'

    @classmethod
    def table_columns(cls):
        return 'code', 'name', 'status', 'created_by:Performed By', 'date_created:Performed On'

    @classmethod
    def get_manage_buttons(cls):
        return []

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details]

    @property
    def details_config(self):
        details = OrderedDict()
        details['name'] = self.name
        details['status'] = self.render_status
        details['Performed By'] = self.created_by
        details['Performed On'] = self.render_performed_on
        details['export_started_on'] = self.render_start_time
        details['export_completed_on'] = self.render_completion_time
        return details

    def details_link_config(self, **kwargs):
        return []

    @classmethod
    def create_task_queue(cls, _name, _query_params, _user=None):
        # First write the task in database
        task = cls()
        task.status = SchedulerTaskQueueEnum.SCHEDULED.value
        task.name = _name
        task.query_params = _query_params
        task.organization = Organization.get_organization_from_cache()
        task.save(using=MC_WRITE_DATABAE_NAME)

        # then push the task into cache
        cache_key = SCHEDULER_TASK_QUEUE_CACHE_KEY
        cached_tasks = CacheManager.get_from_cache_by_key(key=cache_key)
        if cached_tasks is None:
            cached_tasks = list()
        cached_tasks.append({
            'name': _name,
            'query_params': _query_params,
            'organization': task.organization,
            'task_id': task.pk,
            'created_by_id': _user.pk if _user else None,
            'date_created': datetime.now().timestamp() * 1000
        })
        CacheManager.set_cache_element_by_key(key=cache_key, value=cached_tasks, timeout=ONE_DAY_TIMEOUT)

    @property
    def is_downloadable(self):
        generated_export_file = SurveyResponseGeneratedFile.objects.filter(file__name=self.name).first()
        if generated_export_file:
            return ExportFileObject.objects.get(pk=generated_export_file.pk).file_exists
        return False

    @classmethod
    def perform_send_mail(cls, survey_task_queue):
        organization = Organization.objects.filter(is_master=True)[0]
        _user = survey_task_queue.created_by
        email_template, created = EmailTemplate.objects.get_or_create(
            name='Survey Data Export Mails', organization=organization,
            content_structure=
            '<p>Dear [@recipient_users],<br/><br/>[@body]<br/><br/><br/>[@footer]<br/></p>')

        email_body = 'Your survey export file is ready to download. ' \
                     'You can download survey export file from this link:<br/>'

        export_files = ExportFileObject.objects.using(BWDatabaseRouter.get_default_database_name()).filter(
            name=survey_task_queue.name)
        _message = ''
        for _export_file in export_files:
            _file_format = _export_file.extension
            if 'csv' in _file_format.lower() or 'xls' in _file_format.lower():
                _format_specific_message = '   For Excel file: ' + _export_file.get_external_download_link(
                    display_name='download in CSV format')
            else:
                _format_specific_message = '   For SPSS file: ' + _export_file.get_external_download_link(
                    display_name='donwload in SAV format')

            _message += _format_specific_message
            _message += '<br/>'
        _message += '<br/>'
        email_body += _message
        email_body += 'Thank you.'

        html_msg = email_template.content_structure \
            .replace('[@recipient_users]', _user.name) \
            .replace('[@body]', email_body) \
            .replace('[@footer]',
                     '<div style="color:gray;font-style:italic;">'
                     'This is an auto generated email by NUPRP Digital Management System '
                     '(Powered by <a href="http://field.buzz">Field Buzz</a>) on %s</div>'
                     % datetime.now().strftime("%d/%m/%Y %I:%M %p"))

        subject = "Survey Data Export Completed"
        emails = [email_obj.email for email_obj in _user.emails.all()]

        cc = list()

        if emails:
            mail = EmailMultiAlternatives(
                subject=subject,
                body="Survey Data Export",
                from_email=DEFAULT_FROM_EMAIL,
                to=emails,
                cc=cc
            )
            mail.attach_alternative(html_msg, "text/html")
            status = mail.send()

            if status == 1:
                EmailLog.objects.create(status="Success", message="Email sent successfully!", organization=organization,
                                        recipient_user=_user)
            else:
                EmailLog.objects.create(status="Failed", message="Failed to send email.", organization=organization,
                                        recipient_user=_user)

    @classmethod
    def generate_survey_export(cls, given_task=None):
        cache_key = SCHEDULER_TASK_QUEUE_CACHE_KEY
        cached_tasks = CacheManager.get_from_cache_by_key(key=cache_key)
        if cached_tasks is None or len(cached_tasks) < 1:
            executable_task = cls.objects.filter(
                status=SchedulerTaskQueueEnum.SCHEDULED.value).order_by('date_created').first()
            if executable_task is None:
                return False
        else:
            try:
                executable_task = cls.objects.get(pk=cached_tasks[0]['task_id'])
            except:
                return False

        if given_task:
            executable_task = given_task

        _survey_export_processing_tasks = cls.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
            status=SchedulerTaskQueueEnum.PROCESSING.value)

        if not _survey_export_processing_tasks.exists() or given_task:
            task = executable_task
            task.status = SchedulerTaskQueueEnum.PROCESSING.value
            task.start_time = Clock.timestamp()
            task.save(using=MC_WRITE_DATABAE_NAME)

            cached_tasks = cached_tasks[1:] if cached_tasks and len(cached_tasks) else None
            CacheManager.set_cache_element_by_key(key=cache_key, value=cached_tasks, timeout=ONE_DAY_TIMEOUT)

            try:
                _query_params = task.query_params.split(',')
                _time_from = float(_query_params.pop(0))
                _time_to = float(_query_params.pop(0))
                _survey_id = int(_query_params.pop(0))

                # generate survey response excel file
                SurveyResponseGeneratedFile.generate_excel(
                    time_from=_time_from, time_to=_time_to, survey_id=_survey_id, year=None, month_name=None,
                    wards=_query_params, filename=task.name, mode='w'
                )

                # generate survey response sav file
                # SurveyResponseGeneratedFile.generate_sav(
                #     time_from=_time_from, time_to=_time_to, survey_id=_survey_id, year=None, month_name=None,
                #     wards=_query_params, filename=task.name
                # )

                # email sending
                cls.perform_send_mail(task)
                task.status = SchedulerTaskQueueEnum.COMPLETED.value
            except Exception as exp:
                task.status = SchedulerTaskQueueEnum.ERROR.value
                ErrorLog.log(exp)
            task.completion_time = Clock.timestamp()
            task.save(using=MC_WRITE_DATABAE_NAME)

            return True
        return False
