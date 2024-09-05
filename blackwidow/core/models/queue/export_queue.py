"""
    Written by tareq on 7/23/18
"""

from django.apps import apps
from django.db import models

from blackwidow.core.models import ErrorLog
from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.core.models.file.exportfileobject import ExportFileObject
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.queue_element_status_enum import QueueElementStatusEnum
from blackwidow.engine.extensions import Clock

__author__ = 'Tareq'


@decorate(is_object_context,
          route(route='export-queues', group='Import/Export', group_order=30, module=ModuleEnum.Administration,
                display_name="Export Queue", item_order=15))
class ExportQueue(OrganizationDomainEntity):
    """
    This class is used to maintain queue for export service
    """
    user = models.ForeignKey(ConsoleUser, on_delete=models.CASCADE)
    model_name = models.CharField(max_length=127)
    app_label = models.CharField(max_length=127, blank=True)
    queue_args = models.TextField(blank=True)
    queue_kwargs = models.TextField(blank=True)
    queue_request_params = models.TextField(blank=True)
    export_file_name = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=63, blank=True)
    exported_file = models.ForeignKey(ExportFileObject, null=True, on_delete=models.SET_NULL)
    processing_start_time = models.BigIntegerField(default=0)
    processing_completion_time = models.BigIntegerField(default=0)

    class Meta:
        app_label = 'core'

    @classmethod
    def create_export_queue_entry(cls, user, organization, request, app_label, model_name, export_file_name, *args,
                                  **kwargs):
        """
        create an export-queue element to be executed later
        :param user: user instance
        :param organization: organization instance
        :param request: request instance
        :param app_label: app_label for the target model
        :param model_name: name of the target model
        :param args: params
        :param kwargs: extra params
        :return: newly created export queue instance element
        """
        queue_args = repr(args)
        queue_kwargs = repr(kwargs)
        queue_request_params = repr(dict(request.GET))
        export_queue_instance = ExportQueue(
            user=user, organization=organization, app_label=app_label, model_name=model_name,
            export_file_name=export_file_name, queue_args=queue_args, queue_kwargs=queue_kwargs,
            queue_request_params=queue_request_params, status=QueueElementStatusEnum.SCHEDULED.value
        )
        export_queue_instance.save()
        return export_queue_instance

    def perform_export(self):
        from blackwidow.core.generics.views.advanced_export_view import AdvancedGenericExportView
        try:
            self.status = QueueElementStatusEnum.PROCESSING.value
            self.processing_start_time = Clock.now().timestamp() * 1000
            self.save()

            model = apps.get_model(app_label=self.app_label, model_name=self.model_name)
            args = eval(self.queue_args)
            kwargs = eval(self.queue_kwargs)
            search_params = eval(self.queue_request_params)
            filename, path, exported_file_obj = AdvancedGenericExportView.start_background_worker(
                user=self.user, organization=self.organization, model=model, export_file_name=self.export_file_name,
                search_params=search_params, *args, **kwargs)
            self.exported_file = exported_file_obj
            self.status = QueueElementStatusEnum.COMPLETED.value
            self.processing_completion_time = Clock.timestamp()
            self.save()
        except Exception as exp:
            self.status = QueueElementStatusEnum.ERROR.value
            self.processing_completion_time = Clock.timestamp()
            self.save()
            ErrorLog.log(exp=exp)

    @property
    def render_status(self):
        return QueueElementStatusEnum.render(self.status)

    @property
    def render_exported_file(self):
        return self.exported_file if self.exported_file else 'N/A'

    @property
    def render_processing_start_time(self):
        return self.render_timestamp(self.processing_start_time) if self.processing_start_time else 'N/A'

    @property
    def render_processing_completion_time(self):
        return self.render_timestamp(self.processing_completion_time) if self.processing_completion_time else 'N/A'

    @property
    def render_model(self):
        return self.app_label + '.' + self.model_name

    @classmethod
    def table_columns(cls):
        return (
            "render_code", "user", "render_model", "render_status", "render_exported_file", "last_updated"
        )

    @classmethod
    def details_view_fields(cls):
        return [
            'user', 'organization', 'render_model', 'render_status', 'render_exported_file',
            'render_processing_start_time', 'render_processing_completion_time', 'created_by', 'date_created',
            'last_updated_by', 'last_updated']
