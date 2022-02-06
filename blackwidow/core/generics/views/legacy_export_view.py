import json
from datetime import datetime
from random import choice
from string import ascii_uppercase
from urllib import parse

from django.conf import settings
from django.http.request import QueryDict
from django.http.response import HttpResponse
from django.template import loader

from blackwidow.engine.exceptions.exceptions import NotEnoughPermissionException
from blackwidow.engine.extensions import bw_titleize
from blackwidow.engine.extensions.async_task import perform_async
from blackwidow.engine.extensions.clock import Clock
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager
from blackwidow.core.generics.exporter.generic_exporter import GenericExporter
from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.core.mixins.viewmixin.protected_queryset_mixin import ProtectedQuerySetMixin
from blackwidow.core.models import ExporterConfig
from blackwidow.core.models.organizations.organization import Organization

EXPORT_BY_SCHEDULED_SERVICE = getattr(settings, 'EXPORT_BY_SCHEDULED_SERVICE', False)

__author__ = 'Sohel, Ziaul Haque'


class LegacyExportView(GenericListView, ProtectedQuerySetMixin):

    def get_template_names(self):
        """
        :return: list of target templates dedicated to legacy export
        """
        return ['shared/display-templates/_advanced_export_form.html']

    def get_context_data(self, **kwargs):
        _form_class = self.get_form_class()
        context = dict()

        if _form_class:
            context['form'] = _form_class

        context['enable_column_choices'] = False

        return context

    def get_form_class(self):
        """
        :return: model's export dependent form if exists else None
        """
        return self.model.get_export_dependant_fields()

    @classmethod
    def refine_parameters(cls, search_params):
        data_dict = search_params
        refined_GET = {}
        for key, value in data_dict.items():
            if isinstance(value, list):
                value = ",".join(str(x) for x in value)
            if "___" in key:
                id_part = ""
                temp_key = key.replace("___", "")
                if "__" in temp_key:
                    id_part = temp_key[temp_key.find("__") + 2:]

                new_key = key[:key.index("___")]
                new_key = new_key + ":" + id_part
                refined_GET[new_key] = value
            else:
                refined_GET[key] = value
        if not refined_GET:
            return search_params
        params = parse.urlencode(refined_GET)
        return QueryDict(params)

    @classmethod
    def start_background_worker(cls, user, organization, model, export_file_name, search_params,
                                exportable_column_params, *args, **kwargs):
        """
        :param user: requested user instance
        :param organization: organization instance of requested user
        :param model: target model class
        :param export_file_name: export file name (string)
        :param search_params: search parameters
        :param exportable_column_params: exportable columns list
        :param args:
        :param kwargs:
        :return: exported filename, exported file path, exported file object
        """
        organization = organization or kwargs.get('organization', None)
        if not organization:
            organization = Organization.objects.filter(is_master=True).first()

        search_params = cls.refine_parameters(search_params=search_params)
        queryset = cls.get_queryset(user=user, model=model, search_params=search_params, **kwargs)
        try:
            queryset = queryset.filter(organization=organization)
        except:
            pass
        exporter_config = model.exporter_config(
            organization=organization,
            exportable_column_params=exportable_column_params,
            **kwargs
        )

        # TODO check if exporter config is list or model-object
        if isinstance(exporter_config, ExporterConfig):
            # This will support the existing "exporter_config" methods implemented in different places
            exporter_column_config = exporter_config.columns.all().order_by('date_created')
        else:
            exporter_column_config = exporter_config

        filename, path, exported_file_obj = GenericExporter.export_to_excel(
            queryset=queryset, model=model, filename=export_file_name,
            exporter_column_config=exporter_column_config, user=user,
            query_params=search_params, organization=organization, **kwargs
        )
        return filename, path, exported_file_obj

    def handle_export(self, request, organization, export_file_name, *args, **kwargs):
        """
        :param request: request
        :param organization: organization instance of requested user
        :param export_file_name: export filename (string)
        :param args:
        :param kwargs:
        :return: None
        """
        from blackwidow.core.models.queue.export_queue import ExportQueue
        export_queue = ExportQueue.create_export_queue_entry(
            user=request.c_user, organization=organization, request=request, app_label=self.model._meta.app_label,
            model_name=self.model.__name__, export_file_name=export_file_name, *args, **kwargs
        )
        if not EXPORT_BY_SCHEDULED_SERVICE:
            perform_async(method=export_queue.perform_export, args=(export_queue,))

        # notification creation - start
        notification_body = "\"" + bw_titleize(
            self.model_name or self.model.__name__
        ) + "\" data has been successfully exported to file (<i>" + export_file_name + "</i>)."

        # notification_redirect_url = '/export-files/'
        # currently no feature of notification
        # NotificationManager.add_notification_for_user(
        #     notification_body=notification_body,
        #     redirect_url=notification_redirect_url,
        #     request=request
        # )
        # notification creation - end

    def generate_file_name(self, organization):
        """
        :param organization: organization instance of requested user
        :return: filename(string) // format: "exported_[model_name]_[organization.pk]_[datetime]_[random string]
        """
        dttime = datetime.fromtimestamp(Clock.timestamp(_format='s')).strftime('%d%m%Y_%H%M%S')
        random_string = ''.join([choice(ascii_uppercase) for i in range(8)])
        _filename = "exported_" + str(self.model_name or self.model.__name__).replace(" ", "_") + "_" + str(
            organization.pk) + "_" + dttime + "_" + random_string
        return _filename

    def get(self, request, *args, **kwargs):
        if not BWPermissionManager.has_view_permission(self.request, self.model, *args, **kwargs):
            raise NotEnoughPermissionException("You do not have enough permission to view this content.")

        if request.GET.get("get_form") == '1':
            context = self.get_context_data()
            template = loader.get_template(self.get_template_names()[0])
            rendered = template.render(context)
            response = {
                "status": "SUCCESS",
                "message": "Successful"
            }
            if context.get("form", None):
                response["data"] = {
                    "form": rendered
                }
            elif context.get("exportable_columns", None):
                response["data"] = {
                    "exportable_columns": rendered
                }
            else:
                response["data"] = {
                    "form": None,
                    "exportable_columns": None
                }
            return HttpResponse(json.dumps(response))

        _form_class = self.get_form_class()
        advanced_export_form = _form_class(request.GET) if _form_class else None
        if advanced_export_form:
            if advanced_export_form.is_valid():
                file_name = self.generate_file_name(request.c_user.organization)
                self.handle_export(request, request.c_user.organization, file_name, *args, **kwargs)
                response_message = file_name
                return self.render_json_response({
                    'message': response_message,
                    'success': True
                })
            else:
                response_message = '<p style="color: red; padding-left: 13px;">' \
                                   + self.model.__name__ \
                                   + ' advanced export form contains invalid data.</p>'
                return self.render_json_response({
                    'message': response_message,
                    'success': False
                })
        else:
            file_name = self.generate_file_name(request.c_user.organization)
            self.handle_export(request, request.c_user.organization, file_name, *args, **kwargs)
            response_message = file_name
            return self.render_json_response({
                'message': response_message,
                'success': True
            })

    def get_success_url(self):
        return "/" + self.model.get_model_meta('route', 'route') + "/"

    @classmethod
    def get_queryset(cls, user, search_params, model, **kwargs):
        """
        This method prepares the queryset of the objects to be exported
        :param user: user instance who requested the export
        :param search_params: a dictionary, generally request.GET
        :param model: model class
        :param kwargs: extra params
        :return: a queryset instance which returns the objects to be exported
        """
        _queryset = model.get_queryset(
            queryset=model.objects.all(), user=user, profile_filter=not (user.is_super)
        )
        _queryset = user.filter_model(queryset=_queryset)
        _queryset = model.apply_search_filter(search_params=search_params, queryset=_queryset, **kwargs)

        if kwargs.get('proxy_model_name', False):
            _queryset = model.get_proxy_queryset(_queryset, proxy_model_name=kwargs.get('proxy_model_name', ''))

        if kwargs.get('pk'):
            _queryset = _queryset.filter(id=kwargs.get('pk'))

        _queryset = model.get_exportable_queryset(queryset=_queryset)

        return _queryset

    def post(self, request, *args, **kwargs):
        pass
