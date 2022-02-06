from django.views.generic.base import TemplateView

from blackwidow.core.mixins.viewmixin.protected_view_mixin import ProtectedViewMixin
from blackwidow.engine.mixins.viewmixin.json_view_mixin import JsonMixin


__author__ = 'ActiveHigh'


class GenericErrorView(JsonMixin, TemplateView):
    template_name = "shared/error.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['color'] = 'green'
        return context

    def get(self, request, *args, **kwargs):
        return super(GenericErrorView, self).get(request, *args, **kwargs)

    def get_template_names(self):
        return ['shared/error.html']


class GenericInfoView(ProtectedViewMixin, TemplateView):
    template_name = "shared/work_in_progress.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['color'] = 'green'
        return context

    def get(self, request, *args, **kwargs):
        return super(GenericInfoView, self).get(request, *args, **kwargs)

    def get_template_names(self):
        return ['shared/work_in_progress.html']