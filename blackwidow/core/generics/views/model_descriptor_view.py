import json

from django.http.response import HttpResponse
from django.views.generic.base import TemplateView

from blackwidow.core.mixins.viewmixin.protected_view_mixin import ProtectedViewMixin
from blackwidow.engine.decorators.utility import get_models_with_decorator
from blackwidow.engine.extensions.model_descriptor import get_model_description
from settings import INSTALLED_APPS


__author__ = 'ruddra'


class GenericModelDescriptorView(ProtectedViewMixin, TemplateView):
    template_name = 'shared/dashboard.html'
    success_url = '#'

    def get(self, request, *args, **kwargs):
        model_name = request.GET.get('model_name')
        if model_name and model_name != 'None':
            models_with_trigger = get_models_with_decorator('enable_trigger', INSTALLED_APPS)
            for items in models_with_trigger:
                if items == model_name:
                    data = {}
                    data['property_list'] = get_model_description(model_name=model_name, return_property_list=True)
                    return HttpResponse(json.dumps(data), content_type="application/json")
        return super().get(request, *args, **kwargs)
