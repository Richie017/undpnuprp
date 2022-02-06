from django.db.models.query_utils import Q
from django.views.generic.list import ListView

from blackwidow.core.mixins.viewmixin.protected_view_mixin import ProtectedViewMixin
from blackwidow.engine.exceptions.exceptions import NotEnoughPermissionException
from blackwidow.engine.extensions.bw_titleize import bw_titleize
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager

__author__ = 'mahmudul'


class GenericTreeView(ProtectedViewMixin, ListView):
    children_key = 'items'
    parent_key = 'top'
    template_name = 'shared/display-templates/tree.html'

    def get(self, request, *args, **kwargs):
        if not BWPermissionManager.has_view_permission(self.request, self.model):
            raise NotEnoughPermissionException("You do not have enough permission to view this content.")
        return super().get(request, *args, **kwargs)

    def get_template_names(self):
        if self.template_name != '':
            return [self.template_name]
        return ['shared/display-templates/tree.html']

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        queryset = queryset.filter(Q(**{self.parent_key: True}))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['display_model'] = bw_titleize(self.model.__name__) if self.model.get_model_meta('route', 'display_name') is None else  self.model.get_model_meta('route', 'display_name')
        return context

    def flatten_request_parameters(self):
        obj = dict()
        for p in self.request.GET:
            value = self.request.GET.get(p)
            if isinstance(value, list):
                value = value[0]
            if isinstance(value, str):
                try:
                    obj[p] = int(value)
                except ValueError:
                    try:
                        obj[p] = float(value)
                    except ValueError:
                        obj[p] = value

        for p in self.request.POST:
            value = self.request.POST.get(p)
            if isinstance(value, list):
                value = value[0]
            if isinstance(value, str):
                try:
                    obj[p] = int(value)
                except ValueError:
                    try:
                        obj[p] = float(value)
                    except ValueError:
                        obj[p] = value
        return obj

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('format', 'html') == 'json':
            items = list(context['object_list'])
            data = {
                "items": self.json_serialize_array(items, **self.flatten_request_parameters())
            }
            return self.render_json_response(data)
        else:
            return self.response_class(
                request=self.request,
                template=self.get_template_names(),
                context=context,
                **response_kwargs
            )


