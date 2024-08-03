from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

from blackwidow.core.mixins.viewmixin.protected_view_mixin import ProtectedViewMixin


class GenericMutationView(ProtectedViewMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        models = None
        if kwargs.get('ids', '') != '':
            models = self.model.objects.filter(id__in=kwargs.get('ids').split(','))

        if request.GET.get('ids', '') != '':
            models = self.model.objects.filter(id__in=kwargs.get('ids').split(','))

        if models is None:
            if self.is_json_request(request) or request.is_ajax():
                return self.render_json_response({
                    'message':  'Nothing to mutate.',
                    'success': False,
                    'load': 'ajax'
                })
            messages.warning(request, 'Nothing to delete.')
            return redirect(self.get_success_url())

        for m in models:
            m = m.mutate_to()
        if self.is_json_request(request) or request.is_ajax():
            return self.render_json_response({
                'message':  'Request completed successfully.',
                'success': True,
                'load': 'ajax',
                'success_url': self.model.success_url() if hasattr(self.model, 'success_url') else None,
            })
        return redirect(self.get_success_url())
