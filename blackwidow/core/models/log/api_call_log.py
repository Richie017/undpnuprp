import json
import time
import uuid
from collections import OrderedDict
from datetime import datetime

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.engine.constants.cache_constants import LOG_CACHE_PREFIX, ONE_MONTH_TIMEOUT
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.managers.cachemanager import CacheManager

__author__ = 'Tareq, Shuvro'

from blackwidow.engine.routers.database_router import BWDatabaseRouter


@decorate(is_object_context,
          route(route='api-logs', group='Logs', display_name='Api Log', module=ModuleEnum.Settings))
class ApiCallLog(OrganizationDomainEntity):
    url = models.URLField()
    request_type = models.CharField(max_length=500)
    token = models.CharField(max_length=200)
    request_body = models.TextField(default='')
    response_data = models.TextField(default='')
    extra_info = models.TextField(default='')
    start_time = models.BigIntegerField(default=0)
    end_time = models.BigIntegerField(default=0)
    imei_number = models.CharField(max_length=200, blank=True, null=True)
    apk_version = models.CharField(max_length=200, blank=True, null=True)

    @property
    def render_code(self):
        if self.code:
            code_str = self.code
        else:
            code_str = self.code_prefix + '-' + str(self.pk)
        return mark_safe(
            '<a class="inline-link" href="' + reverse(self.true_route_name(ViewActionEnum.Details),
                                                      kwargs={'pk': self.pk}) + '">' + code_str + '</a>')

    @property
    def render_created_by(self):
        if self.created_by_id:
            return self.created_by
        return self.last_updated_by

    @classmethod
    def table_columns(cls):
        return 'render_code', 'url', 'request_type', 'response_data', 'render_IMEI_number', 'render_APK_version', \
               'render_server_processing_time', 'render_created_by', 'date_created', 'last_updated'

    @property
    def render_IMEI_number(self):
        return self.imei_number if self.imei_number else 'N/A'

    @property
    def render_APK_version(self):
        return self.apk_version if self.apk_version else 'N/A'

    @property
    def details_config(self):
        detail = OrderedDict()
        detail['code'] = self.code
        detail['request_url'] = self.url
        detail['request_type'] = self.request_type
        detail['IMEI Number'] = self.render_IMEI_number
        detail['APK version'] = self.render_APK_version
        detail['server_processing_time'] = self.render_server_processing_time
        detail['token'] = self.token
        detail['raw_request_body'] = self.request_body
        detail['response_data'] = self.response_data
        detail['extra_info'] = self.extra_info
        detail['processing_start_time'] = self.render_timestamp(self.start_time)
        detail['processing_end_time'] = self.render_timestamp(self.end_time)
        detail['date_created'] = self.render_timestamp(self.date_created)
        detail['last_updated'] = self.render_timestamp(self.last_updated)
        detail['created_by'] = self.created_by
        return detail

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Delete]

    @property
    def render_server_processing_time(self):
        return str(float(self.end_time - self.start_time) / 1000) + 's'

    @property
    def render_start_time(self):
        return self.render_timestamp(self.start_time)

    @property
    def render_end_time(self):
        return self.render_timestamp(self.end_time)

    @property
    def get_inline_manage_buttons(self):
        return [dict(
            name='Details',
            action='view',
            title="Click to view this item",
            icon='icon-eye',
            ajax='0',
            url_name=self.__class__.get_route_name(action=ViewActionEnum.Details),
            classes='all-action ',
            parent=None
        )]

    def details_link_config(self, **kwargs):
        return []

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details, ViewActionEnum.Delete]

    @classmethod
    def get_routes(cls, **kwargs):
        return [ViewActionEnum.Details, ViewActionEnum.Edit, ViewActionEnum.Delete, ViewActionEnum.Manage]

    def save_log(self):
        if hasattr(settings, 'CACHE_LOGS') and getattr(settings, 'CACHE_LOGS', False):
            log_cache_key = LOG_CACHE_PREFIX + self.__class__.__name__
            log_cache_dict = CacheManager.get_from_cache_by_key(key=log_cache_key)
            if log_cache_dict is None:
                log_cache_dict = dict()
            log_cache_dict[self.tsync_id] = self
            CacheManager.set_cache_element_by_key(key=log_cache_key, value=log_cache_dict, timeout=ONE_MONTH_TIMEOUT)
        else:
            self.save()

    @classmethod
    def log(cls, *args, url='', type='', token='', log_instance=None,
            request=None, response=None, extra_info='', log_time=None, **kwargs):
        if request.method.lower() == 'get':
            if hasattr(settings, 'LOG_GET_API_CALLS') and getattr(settings, 'LOG_GET_API_CALLS') == False:
                return None
        try:
            current_timestamp = datetime.now().timestamp() * 1000
            organization = kwargs.get('organization', Organization.get_organization_from_cache())
            if log_instance:
                log = log_instance
            else:
                log = cls(tsync_id=uuid.uuid4(), organization=organization, type=cls.__name__)
                try:
                    log.being_processed = True
                    log.date_created = current_timestamp
                    log.last_updated = current_timestamp
                    log.created_by_id = request.c_user.id
                    log.last_updated_by_id = request.c_user.id
                except:
                    pass
            try:
                if log_time is True:  # Start Time
                    log.start_time = int(time.time() * 1000)
                elif log_time is False:  # End Time
                    log.end_time = int(time.time() * 1000)
            except:
                pass
            log.url = url if url != '' else request.META['PATH_INFO']
            log.organization = organization
            try:
                if hasattr(request, 'c_user'):
                    log.created_by = request.c_user
                    log.last_updated_by = request.c_user
                log.token = request.user.auth_token.key
            except:
                pass
            log.request_type = type
            if hasattr(request, 'method'):
                log.request_type = request.method
            if (log.request_body is None or log.request_body == '') and \
                    hasattr(request, 'GET') and request.method.lower() == 'get':
                try:
                    log.request_body = json.dumps(request.GET)
                except:
                    pass
                log.request_type = type if type != '' else 'GET'
            elif hasattr(request, 'POST') and request.method.lower() in ['post', 'put']:
                try:
                    if hasattr(request, 'body'):
                        log.request_body = json.dumps(json.loads(request.body.decode("utf-8")))
                except:
                    pass
                log.request_type = type if type != '' else request.method.upper()

            try:
                if hasattr(request, 'META'):
                    imei_number = request.META.get('HTTP_IMEI_NUMBER', None)
                    if imei_number is not None:
                        log.imei_number = imei_number
            except:
                pass
            try:
                if hasattr(request, 'META'):
                    apk_version = request.META.get('HTTP_APK_VERSION', None)
                    if apk_version is not None:
                        log.apk_version = apk_version
            except:
                pass

            if response:
                log.response_data = str(response.status_code) + ' ' + response.status_text
            if extra_info and extra_info != '':
                log.extra_info = extra_info
            log.save_log()
            return log
        except Exception as exp:
            ErrorLog.log(exp)
            return None
