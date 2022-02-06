from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import DetailView

from blackwidow.core.managers.contextmanager import ContextManager
from blackwidow.core.mixins.viewmixin.protected_view_mixin import ProtectedViewMixin
from blackwidow.engine.exceptions.exceptions import NotEnoughPermissionException
from blackwidow.engine.extensions.object_version import get_object_if_version_requested
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager
from blackwidow.engine.routers.database_router import BWDatabaseRouter

__author__ = 'mahmudul'


class GenericDetailsView(ProtectedViewMixin, DetailView):
    template_name = ""
    success_url = "/"
    model_name = ''
    model = None
    object = None

    master_object = None
    version_detail = False

    def get_queryset(self, **kwargs):
        kwargs.update(add_versions=True)
        return super(GenericDetailsView, self).get_queryset(**kwargs)

    @method_decorator(login_required)
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        if self.model is not None:
            if not BWPermissionManager.has_view_permission(self.request, self.model):
                user = ContextManager.get_current_user(self.request)
                if 'pk' in kwargs and not user['id'] == int(kwargs.get("pk", "0")) \
                        and self.model.__name__ != 'ConsoleUser':
                    raise NotEnoughPermissionException("You do not have enough permission to view this item.")

                if 'id' in kwargs and not user['id'] == int(kwargs.get("id", "0")) \
                        and self.model.__name__ != 'ConsoleUser':
                    raise NotEnoughPermissionException("You do not have enough permission to view this item.")
        return super(ProtectedViewMixin, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        object = super(GenericDetailsView, self).get_object(queryset=queryset)
        version_object = get_object_if_version_requested(
            request=self.request,
            model=self.model,
            object=object
        )
        if version_object:
            self.version_detail = True
            self.master_object = object
            return version_object
        return object

    def get_context_data(self, **kwargs):
        context = super(GenericDetailsView, self).get_context_data(**kwargs)
        context['data'] = self.object
        context['model_meta']['tabs'] = self.object.tabs_config
        details_config = self.object.details_config

        if not self.version_detail:
            if any(filter(lambda x: x.__name__ == 'is_object_context', self.model._decorators)):
                context['details_link_config'] = self.details_link_config()
            else:
                context['details_link_config'] = \
                    self.object.details_link_config(
                        user=self.request.c_user
                    )
        else:
            context['app_pabel'] = self.model._meta.app_label
            context['model_name'] = self.model.__name__
            context['master_object'] = self.master_object
            context['model_meta']['properties']['current_version'] = str(context['master_object'])
            context['details_link_config'] = [
                dict(
                    name='Restore Version',
                    classes='restore-action',
                    action='restore',
                    icon='fbx-rightnav-tick',
                    ajax='1',
                    url_name='restore_version'
                )
            ]

        try:
            model = self.model
            if model._decorators is not None:
                for decorator in model._decorators:
                    if decorator.__name__ == "enable_versioning":
                        version_dict = OrderedDict()
                        version_dict["versions"] = self.object.render_versions
                        details_config["version_information"] = version_dict
        except Exception as e:
            from blackwidow.core.models import ErrorLog
            ErrorLog.log(exp=e)

        context['model_meta']['properties'] = details_config
        return context

    def get_template_names(self):
        if self.template_name != '':
            return [self.template_name]
        self.model_name = self.model_name if self.model_name else self.model.__name__.lower()
        return [
            self.model_name.lower().replace(' ', "_") + '/details.html',
            "shared/display-templates/details.html"
        ]

    def render_to_response(self, context, *args, **response_kwargs):
        if self.request.GET.get('format', 'html') == 'json':
            data = self.json_serialize_object(context['data'])
            return self.render_json_response(data)
        else:
            if 'template_name' in response_kwargs:
                return self.response_class(
                    request=self.request,
                    template=response_kwargs['template_name'],
                    context=context,
                    **response_kwargs
                )

            return self.response_class(
                request=self.request,
                template=self.get_template_names(),
                context=context,
                **response_kwargs
            )
