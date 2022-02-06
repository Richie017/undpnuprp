import json
from datetime import datetime
from multiprocessing.synchronize import Lock
from threading import Thread
from urllib.parse import urlencode

from django.http.request import QueryDict
from django.http.response import HttpResponse
from django.template import Context
from django.template import loader

from blackwidow.core.generics.exporter.generic_exporter import GenericExporter
from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.core.mixins.viewmixin.protected_queryset_mixin import ProtectedQuerySetMixin
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.engine.exceptions.exceptions import NotEnoughPermissionException
from blackwidow.engine.extensions.clock import Clock
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager
from blackwidow.engine.routers.database_router import BWDatabaseRouter

__author__ = 'Sohel'


class AdvancedGenericExportView(GenericListView, ProtectedQuerySetMixin):

    def get_template_names(self):
        return ['shared/display-templates/_advanced_export_form.html']

    def get_context_data(self, **kwargs):
        advanced_export_form = None
        if self.model.get_export_dependant_fields():
            advanced_export_form = self.model.get_export_dependant_fields()()
        context = Context({"form": advanced_export_form})
        return context

    def get_form_class(self):
        return self.model.get_export_dependant_fields()

    def refine_parameters(self, request):
        data_dict = request.GET
        refined_GET = {}
        for key, value in data_dict.items():
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
            return request.GET
        params = urlencode(refined_GET)
        qdict = QueryDict(params)
        return qdict

    def start_background_worker(self, request, organization, export_file_name, *args, **kwargs):
        if not organization:
            organization = Organization.objects.first()
        request.GET = self.refine_parameters(request)
        queryset = self.get_queryset(request, **kwargs)
        exporter_config = self.model.exporter_config(organization=organization, **kwargs)
        filename, path = GenericExporter.export_to_excel(
            queryset=queryset, model=self.model,
            filename=export_file_name,
            exporter_config=exporter_config,
            user=request.c_user, query_params=request.GET,
            **kwargs
        )

    def handle_export(self, request, organization, export_file_name, *args, **kwargs):
        lock = Lock(ctx=None)
        lock.acquire(True)
        process = Thread(
            target=self.start_background_worker,
            args=(request, organization, export_file_name, args, kwargs,)
        )
        process.start()
        lock.release()

    def generate_file_name(self):
        dttime = datetime.fromtimestamp(Clock.timestamp(_format='s')).strftime('%d%m%Y_%H%M%S')
        dest_filename = str(self.model.__name__) + '_' + dttime
        return dest_filename

    def get(self, request, *args, **kwargs):
        if not BWPermissionManager.has_view_permission(self.request, self.model):
            raise NotEnoughPermissionException("You do not have enough permission to view this content.")

        if request.GET.get("get_form") == '1':
            context = self.get_context_data()
            if context.get("form"):
                template = loader.get_template(self.get_template_names()[0])
                context = Context(context)
                rendered = template.render(context)
                response = {
                    "status": "SUCCESS",
                    "message": "Successful",
                    "data": {
                        "form": rendered
                    }
                }
                return HttpResponse(json.dumps(response))
            else:
                response = {
                    "status": "SUCCESS",
                    "message": "Successful",
                    "data": {
                        "form": 0
                    }
                }
                return HttpResponse(json.dumps(response))

        advanced_export_form = self.model.get_export_dependant_fields()(
            request.GET) if self.model.get_export_dependant_fields() else None
        if advanced_export_form:
            if advanced_export_form.is_valid():
                file_name = self.generate_file_name()
                self.handle_export(request, request.c_user.organization, file_name, *args, **kwargs)
                response_message = file_name
                return self.render_json_response({
                    'message': response_message,
                    'success': True
                })
            else:
                response_message = '<p style="color: red; padding-left: 13px;">' + self.model.__name__ + ' advanced export form contains invalid data.</p>'
                return self.render_json_response({
                    'message': response_message,
                    'success': False
                })
        else:
            file_name = self.generate_file_name()
            self.handle_export(request, request.c_user.organization, file_name, *args, **kwargs)
            response_message = file_name
            return self.render_json_response({
                'message': response_message,
                'success': True
            })

    def get_success_url(self):
        return "/" + self.model.get_model_meta('route', 'route') + "/"

    def get_queryset(self, request, **kwargs):
        _user = request.c_user.to_business_user()
        _queryset = self.model.get_queryset(
            queryset=self.model.objects.using(BWDatabaseRouter.get_export_database_name()).all(),
            user=_user,
            profile_filter=not (_user.is_super)
        )
        _queryset = _user.filter_model(request=request, queryset=_queryset)
        return self.model.apply_search_filter(request.GET, queryset=_queryset, **kwargs)

    def post(self, request, *args, **kwargs):
        pass
